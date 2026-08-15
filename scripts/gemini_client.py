"""Gemini API bilan ishlash: mavzu izlash + post yozish (Google Search bilan),
sifat nazorati (QC), va rasm generatsiyasi (Nano Banana / gemini-*-image)."""
import base64
import json
import re

import requests

import config

GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


def _generate_content(model: str, contents: list, tools: list | None = None,
                       response_mime_type: str | None = None,
                       response_modalities: list | None = None,
                       timeout: int = 90) -> dict:
    url = f"{GEMINI_BASE}/{model}:generateContent"
    headers = {"x-goog-api-key": config.GEMINI_API_KEY, "Content-Type": "application/json"}
    body = {"contents": contents}
    if tools:
        body["tools"] = tools
    generation_config = {}
    if response_mime_type:
        generation_config["responseMimeType"] = response_mime_type
    if response_modalities:
        generation_config["responseModalities"] = response_modalities
    if generation_config:
        body["generationConfig"] = generation_config

    resp = requests.post(url, headers=headers, data=json.dumps(body), timeout=timeout)
    if resp.status_code != 200:
        raise RuntimeError(
            f"Gemini API xatosi ({model}): HTTP {resp.status_code} - {resp.text[:1000]}"
        )
    return resp.json()


def _extract_text(response: dict) -> str:
    try:
        parts = response["candidates"][0]["content"]["parts"]
        texts = [p.get("text", "") for p in parts if "text" in p]
        return "\n".join(t for t in texts if t).strip()
    except (KeyError, IndexError) as exc:
        raise RuntimeError(f"Gemini javobidan matn topilmadi: {json.dumps(response)[:800]}") from exc


def generate_topic_and_post(used_topics: list[str]) -> dict:
    """1 va 2-agent: internetdan yangi mavzu izlaydi va postni yozadi.
    Qaytaradi: {"topic": str, "post_text": str, "image_prompt": str, "audio_text": str}
    """
    avoid_list = "\n".join(f"- {t}" for t in used_topics[-60:]) or "(hali hech narsa yo'q)"

    prompt = f"""
Sen "{config.CHANNEL_BRAND}" nomli Telegram kanali uchun kontent tayyorlovchi yordamchisan.
Kanal yo'nalishi: {config.RUBRIKA}

Vazifa:
1. Google Search orqali Claude AI (Anthropic)ning joriy imkoniyatlari, foydalanish usullari yoki amaliy
   promptlash texnikalari haqida ISHONCHLI va DOLZARB bitta aniq mavzu top. Mavzu quyidagi ro'yxatda
   allaqachon ishlatilganlardan FARQ QILISHI SHART:
{avoid_list}
2. Shu mavzu asosida Telegram posti yoz. Post o'zbek tilida bo'lishi kerak.

{config.POST_STYLE_GUIDE}

Javobni FAQAT quyidagi JSON formatida qaytar (boshqa hech qanday matn, izoh yoki markdown bo'lmasin):
{{
  "topic": "mavzuning qisqa nomi (5-8 so'z, tarixga yozib qo'yish uchun)",
  "post_text": "to'liq tayyor Telegram posti matni (emoji va hashtaglar bilan)",
  "image_prompt": "shu post uchun mos, matnsiz, zamonaviy va minimalistik illyustrativ rasm uchun inglizcha tavsif (rasm generatsiya modeliga beriladi)",
  "audio_text": "postning audio o'qish uchun moslashtirilgan versiyasi - hashtag va emojilarsiz, tabiiy gapiriladigan uslubda, 400-700 belgi"
}}
"""

    response = _generate_content(
        config.GEMINI_TEXT_MODEL,
        contents=[{"parts": [{"text": prompt}]}],
        tools=[{"google_search": {}}],
    )
    raw_text = _extract_text(response)
    return _parse_json_block(raw_text)


def _parse_json_block(raw_text: str) -> dict:
    # Model ba'zan ```json ... ``` bilan o'rab yuborishi mumkin - tozalaymiz.
    cleaned = re.sub(r"^```(json)?|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()
    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if not match:
        raise RuntimeError(f"JSON topilmadi Gemini javobida: {raw_text[:800]}")
    return json.loads(match.group(0))


def qc_check(post_text: str) -> dict:
    """5-agent: sifat nazorati. Qaytaradi {"ok": bool, "reason": str}."""
    prompt = f"""
Quyidagi Telegram post matnini sifat nazoratidan o'tkaz. Post "{config.CHANNEL_BRAND}" kanali uchun,
yo'nalishi: {config.RUBRIKA}

Tekshirish mezonlari:
- O'zbek tilida grammatik xatolarsiz yozilganmi?
- Rubrikaga (Claude AI dan foydalanish maslahati) mos keladimi?
- Aniq va amaliy foydali maslahat beradimi (umumiy gap emas)?
- Uzunligi maqbulmi (400-1300 belgi oralig'ida)?
- Soxta da'vo, reklama, siyosiy/diniy mazmun yo'qmi?
- Ton do'stona va professionalmi?

POST MATNI:
---
{post_text}
---

Javobni FAQAT JSON formatida qaytar: {{"ok": true yoki false, "reason": "qisqa asos (o'zbek tilida)"}}
"""
    response = _generate_content(config.GEMINI_TEXT_MODEL, contents=[{"parts": [{"text": prompt}]}])
    raw_text = _extract_text(response)
    return _parse_json_block(raw_text)


def generate_image(image_prompt: str) -> bytes:
    """3-agent: Nano Banana (Gemini native image) orqali rasm generatsiya qiladi."""
    full_prompt = (
        f"{image_prompt}. Style: clean, modern, minimalistic, flat illustration, soft color "
        f"palette, no embedded text or letters in the image, square aspect ratio, suitable for "
        f"a professional tech-tips social media post."
    )
    response = _generate_content(
        config.GEMINI_IMAGE_MODEL,
        contents=[{"parts": [{"text": full_prompt}]}],
        response_modalities=["TEXT", "IMAGE"],
    )
    try:
        parts = response["candidates"][0]["content"]["parts"]
    except (KeyError, IndexError) as exc:
        raise RuntimeError(f"Gemini rasm javobi noto'g'ri formatda: {json.dumps(response)[:800]}") from exc

    for part in parts:
        inline = part.get("inlineData") or part.get("inline_data")
        if inline and inline.get("data"):
            return base64.b64decode(inline["data"])

    raise RuntimeError(f"Gemini javobida rasm topilmadi: {json.dumps(response)[:800]}")
