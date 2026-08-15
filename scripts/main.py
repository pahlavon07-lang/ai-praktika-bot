"""Asosiy orkestrator: 1-6 barcha "agentlar"ni ketma-ket ishga tushiradi.

Oqim:
1-2) Gemini: mavzu izlash (Google Search bilan) + post yozish
3) Gemini: rasm generatsiya (Nano Banana)
4) ElevenLabs: audio generatsiya
5) Gemini: sifat nazorati (QC) - agar rad etilsa, qaytadan yozadi (limitgacha)
   -> admin'ga preview yuboriladi, WAIT_MINUTES davomida "Qayta qilish" / "Hoziroq
      chiqarish" tugmalari kutiladi
6) Telegram: kanalga chiqarish (agar tugma bosilmasa - avtomatik; "Qayta qilish"
   bosilsa - butun oqim qaytadan boshidan ishlaydi va tayyor bo'lgach, vaqtidan
   qat'iy nazar, kanalga chiqariladi)
"""
import sys
import traceback

import config
import gemini_client
import history
import telegram_client
from elevenlabs_client import generate_audio


def build_one_post() -> dict:
    """To'liq bitta postni tayyorlaydi: mavzu+matn+rasm+audio+QC. QC o'tmasa,
    MAX_REGENERATE_ATTEMPTS marta qayta urinadi."""
    used_topics = history.load()
    last_error = None

    for attempt in range(1, config.MAX_REGENERATE_ATTEMPTS + 1):
        try:
            draft = gemini_client.generate_topic_and_post(used_topics)
            qc = gemini_client.qc_check(draft["post_text"])
            if not qc.get("ok"):
                print(f"[QC RAD ETDI - urinish {attempt}] Sabab: {qc.get('reason')}")
                used_topics = used_topics + [draft["topic"]]  # qayta urinishda shu mavzuni ham tashla
                continue

            image_bytes = gemini_client.generate_image(draft["image_prompt"])
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

    raise RuntimeError(f"{config.MAX_REGENERATE_ATTEMPTS} marta urinishdan keyin ham post tayyor bo'lmadi: {last_error}")


def run() -> None:
    missing = [
        name for name in [
            "TELEGRAM_BOT_TOKEN", "GEMINI_API_KEY", "ELEVENLABS_API_KEY",
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
