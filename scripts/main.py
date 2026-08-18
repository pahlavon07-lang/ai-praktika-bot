"""Asosiy orkestrator: 1-6 barcha "agentlar"ni ketma-ket ishga tushiradi.

Oqim:
1-2) Groq (bepul, kartasiz LLM): mavzu tanlash + post yozish
3) Lokal PIL: rasm generatsiya (tashqi API'ga bog'liq emas, har doim ishlaydi)
4) ElevenLabs: audio generatsiya
5) Groq: sifat nazorati (QC) - agar rad etilsa, qaytadan yozadi (limitgacha)
   -> admin'ga preview yuboriladi, WAIT_MINUTES davomida "Qayta qilish" / "Hoziroq
      chiqarish" tugmalari kutiladi
6) Telegram: kanalga chiqarish (agar tugma bosilmasa - avtomatik; "Qayta qilish"
   bosilsa - butun oqim qaytadan boshidan ishlaydi va tayyor bo'lgach, vaqtidan
   qat'iy nazar, kanalga chiqariladi)
"""
import hashlib
import io
import sys
import textwrap
import time
import traceback

from PIL import Image, ImageDraw, ImageFont

import config
import groq_client
import history
import telegram_client
from aisha_client import generate_audio


# --- Zaxira (fallback) rasm generatori ---
# SABAB: Google bepul tarifida Nano Banana (Gemini rasm) modellari uchun kvota
# odatda 0 (nol) bo'ladi - ya'ni bepul kalit bilan Gemini orqali rasm
# generatsiya qilib BO'LMAYDI. Shuning uchun bu yerda oddiy, lekin chiroyli
# "kartochka" ko'rinishidagi rasm PIL bilan lokal tarzda, internet kerak
# bo'lmasdan yaratiladi - bu har doim ishlaydi.

_IMG_SIZE = (1024, 1024)
_PALETTES = [
    ((45, 52, 122), (110, 74, 196)),
    ((14, 98, 122), (60, 176, 176)),
    ((92, 46, 145), (198, 88, 158)),
    ((20, 90, 70), (110, 190, 120)),
    ((150, 60, 40), (230, 150, 60)),
]
_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]


def _load_font(size: int):
    for path in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _gradient(size, top_color, bottom_color):
    width, height = size
    base = Image.new("RGB", size, top_color)
    draw = ImageDraw.Draw(base)
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return base


def generate_fallback_image(title: str, brand: str = "AI Praktika") -> bytes:
    seed = int(hashlib.sha256(title.encode("utf-8")).hexdigest(), 16)
    top_color, bottom_color = _PALETTES[seed % len(_PALETTES)]

    img = _gradient(_IMG_SIZE, top_color, bottom_color)
    draw = ImageDraw.Draw(img)

    title_font = _load_font(64)
    brand_font = _load_font(32)

    wrapped = textwrap.fill(title, width=18)
    lines = wrapped.split("\n")

    line_heights = []
    total_height = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        h = bbox[3] - bbox[1]
        line_heights.append(h)
        total_height += h + 20

    y = (_IMG_SIZE[1] - total_height) / 2
    for line, h in zip(lines, line_heights):
        bbox = draw.textbbox((0, 0), line, font=title_font)
        w = bbox[2] - bbox[0]
        x = (_IMG_SIZE[0] - w) / 2
        draw.text((x + 3, y + 3), line, font=title_font, fill=(0, 0, 0, 80))
        draw.text((x, y), line, font=title_font, fill=(255, 255, 255))
        y += h + 20

    brand_bbox = draw.textbbox((0, 0), brand, font=brand_font)
    brand_w = brand_bbox[2] - brand_bbox[0]
    draw.text(((_IMG_SIZE[0] - brand_w) / 2, _IMG_SIZE[1] - 90), brand, font=brand_font, fill=(255, 255, 255))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _is_quota_error(exc: Exception) -> bool:
    text = str(exc)
    return "429" in text or "quota" in text.lower() or "too_many_requests" in text.lower()


def build_one_post() -> dict:
    """To'liq bitta postni tayyorlaydi: mavzu+matn+rasm+audio+QC. QC o'tmasa,
    MAX_REGENERATE_ATTEMPTS marta qayta urinadi. Kvota xatosida uzoqroq
    kutib, keyin qayta urinadi - kvotani behuda sarflamaslik uchun.

    Matn/QC uchun Groq (bepul, kartasiz) ishlatiladi. Rasm uchun to'g'ridan-to'g'ri
    lokal PIL generatori ishlatiladi (tashqi API'ga bog'liq emas, har doim ishlaydi)."""
    used_topics = history.load()
    last_error = None

    for attempt in range(1, config.MAX_REGENERATE_ATTEMPTS + 1):
        try:
            draft = groq_client.generate_topic_and_post(used_topics)
            qc = groq_client.qc_check(draft["post_text"])
            if not qc.get("ok"):
                print(f"[QC RAD ETDI - urinish {attempt}] Sabab: {qc.get('reason')}")
                used_topics = used_topics + [draft["topic"]]  # qayta urinishda shu mavzuni ham tashla
                continue

            image_bytes = generate_fallback_image(draft["topic"])
            audio_bytes = generate_audio(draft["audio_text"])

            return {
                "topic": draft["topic"],
                "post_text": draft["post_text"],
                "image_bytes": image_bytes,
                "audio_bytes": audio_bytes,
            }
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            print(f"[XATO - urinish {attempt}] {exc}")
            traceback.print_exc()
            if attempt < config.MAX_REGENERATE_ATTEMPTS:
                wait_seconds = 45 if _is_quota_error(exc) else 5
                print(f"[KUTISH] {wait_seconds} soniya kutib, qayta urinamiz...")
                time.sleep(wait_seconds)

    raise RuntimeError(f"{config.MAX_REGENERATE_ATTEMPTS} marta urinishdan keyin ham post tayyor bo'lmadi: {last_error}")


def run() -> None:
    missing = [
        name for name in [
            "TELEGRAM_BOT_TOKEN", "GROQ_API_KEY", "AISHA_API_KEY",
            "CHANNEL_USERNAME", "ADMIN_CHAT_ID",
        ]
        if not getattr(config, name)
    ]
    if missing:
        print(f"XATO: quyidagi sozlamalar yo'q: {missing}")
        sys.exit(1)

    post = build_one_post()
    print(f"Post tayyor. Mavzu: {post['topic']}")

    preview = telegram_client.send_preview(post["post_text"], post["image_bytes"], post["audio_bytes"])
    history.append(post["topic"])

    decision = telegram_client.poll_for_decision(preview["control_message_id"], config.WAIT_MINUTES)

    if decision == telegram_client.BTN_PUBLISH_NOW or decision is None:
        telegram_client.publish_to_channel(post["post_text"], preview["photo_file_id"], preview["audio_file_id"])
        telegram_client.notify_admin(f"✅ Post {config.CHANNEL_USERNAME} kanaliga chiqarildi.")
        print("Post kanalga chiqarildi.")
        return

    if decision == telegram_client.BTN_REDO:
        telegram_client.notify_admin("\U0001F504 Qayta qilinmoqda... tayyor bo'lgach yana yuboraman.")
        print("Foydalanuvchi 'Qayta qilish'ni bosdi. Yangi post tayyorlanmoqda...")
        new_post = build_one_post()
        new_preview = telegram_client.send_preview(new_post["post_text"], new_post["image_bytes"], new_post["audio_bytes"])
        history.append(new_post["topic"])
        # Qayta qilingan post uchun ham xuddi shu tanlov oynasi beriladi.
        second_decision = telegram_client.poll_for_decision(new_preview["control_message_id"], config.WAIT_MINUTES)
        if second_decision == telegram_client.BTN_REDO:
            telegram_client.notify_admin(
                "Yana \"Qayta qilish\" bosildi, lekin bu safar avtomatik oqim faqat 2 marta qayta urinadi. "
                "Yuqoridagi oxirgi post baribir kanalga chiqariladi."
            )
        telegram_client.publish_to_channel(new_post["post_text"], new_preview["photo_file_id"], new_preview["audio_file_id"])
        telegram_client.notify_admin(f"✅ Qayta tayyorlangan post {config.CHANNEL_USERNAME} kanaliga chiqarildi.")
        print("Qayta tayyorlangan post kanalga chiqarildi.")
        return


if __name__ == "__main__":
    run()
