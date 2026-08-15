"""Gemini API (Interactions API, 2026 formati) bilan ishlash: mavzu izlash +
post yozish (Google Search bilan), sifat nazorati (QC), va rasm generatsiyasi
(Nano Banana / gemini-*-image).

ESLATMA: Google 2026 yilda eski "generateContent" API'sini yangi
foydalanuvchilar uchun yopib, "Interactions API" ga o'tkazdi. Agar bu yerda
yana 404/"model topilmadi" yoki boshqa formatga oid xato chiqsa,
https://ai.google.dev/gemini-api/docs/interactions-overview sahifasini
tekshiring - API strukturasi yana o'zgargan bo'lishi mumkin.
"""
import base64
import json
import re

import requests

import config

INTERACTIONS_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"


def _call_interactions(model: str, input_text: str, tools: list | None = None, timeout: int = 90) -> dict:
    headers = {"x-goog-api-key": config.GEMINI_API_KEY, "Content-Type": "application/json"}
    body = {"model": model, "input": input_text}
    if tools:
        body["tools"] = tools

    resp = requests.post(INTERACTIONS_URL, headers=headers, data=json.dumps(body), timeout=timeout)
    if resp.status_code != 200:
        raise RuntimeError(
            f"Gemini API xatosi ({model}): HTTP {resp.status_code} - {resp.text[:1200]}"
        )
    return resp.json()


def _extract_text(response: dict) -> str:
    if response.get("output_text"):
        return response["output_text"].strip()

    texts = []
    for step in response.get("steps", []):
        if step.get("type") != "model_output":
            continue
        for item in step.get("content", []):
            if item.get("type") == "text" and item.get("text"):
                texts.append(item["text"])
    result = "\n".join(t for t in texts if t).strip()
    if not result:
        raise RuntimeError(f"Gemini javobidan matn topilmadi: {json.dumps(response)[:1200]}")
    return result


def _extract_image_bytes(response: dict) -> bytes:
    for step in response.get("steps", []):
        if step.get("type") != "model_output":
            continue
        for item in step.get("content", []):
            if item.get("type") == "image" and item.get("data"):
                return base64.b64decode(item["data"])
    raise RuntimeError(f"Gemini javobida rasm topilmadi: {json.dumps(response)[:1200]}")


def _parse_json_block(raw_text: str) -> dict:
    cleaned = re.sub(r"^```(json)?|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()
    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if not match:
        raise RuntimeError(f"JSON topilmadi Gemini javobida: {raw_text[:1200]}")
    return json.loads(match.group(0))


def generate_topic_and_post(used_topics: list[str]) -> dict:
    """1 va 2-agent: internetdan yangi mavzu izlaydi va postni yozadi."""
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
    response = _call_interactions(
        config.GEMINI_TEXT_MODEL,
        input_text=prompt,
        tools=[{"type": "google_search"}],
    )
    raw_text = _extract_text(response)
    return _parse_json_block(raw_text)


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
    response = _call_interactions(config.GEMINI_TEXT_MODEL, input_text=prompt)
    raw_text = _extract_text(response)
    return _parse_json_block(raw_text)


def generate_image(image_prompt: str) -> bytes:
    """3-agent: Nano Banana (Gemini native image) orqali rasm generatsiya qiladi."""
    full_prompt = (
        f"{image_prompt}. Style: clean, modern, minimalistic, flat illustration, soft color "
        f"palette, no embedded text or letters in the image, square aspect ratio, suitable for "
        f"a professional tech-tips social media post."
    )
    response = _call_interactions(config.GEMINI_IMAGE_MODEL, input_text=full_prompt)
    return _extract_image_bytes(response)
