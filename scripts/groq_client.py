"""Groq API (bepul, kartasiz) bilan matn generatsiyasi: mavzu+post yozish va
sifat nazorati (QC). OpenAI-mos ("OpenAI-compatible") chat completions
formatida ishlaydi.
"""
import json
import re

import requests

import config

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def _chat(prompt: str, timeout: int = 90) -> str:
    headers = {
        "Authorization": f"Bearer {config.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": config.GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8,
    }
    resp = requests.post(GROQ_URL, headers=headers, data=json.dumps(body), timeout=timeout)
    if resp.status_code != 200:
        raise RuntimeError(f"Groq API xatosi ({config.GROQ_MODEL}): HTTP {resp.status_code} - {resp.text[:1200]}")
    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError) as exc:
        raise RuntimeError(f"Groq javobidan matn topilmadi: {json.dumps(data)[:1200]}") from exc


def _parse_json_block(raw_text: str) -> dict:
    cleaned = re.sub(r"^```(json)?|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()
    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if not match:
        raise RuntimeError(f"JSON topilmadi Groq javobida: {raw_text[:1200]}")
    return json.loads(match.group(0))


def generate_topic_and_post(used_topics: list[str]) -> dict:
    """1 va 2-agent: mavzu tanlaydi va postni yozadi (o'z bilimi asosida,
    internet qidiruvisiz - Groq'da tashqi qidiruv vositasi yo'q)."""
    avoid_list = "\n".join(f"- {t}" for t in used_topics[-60:]) or "(hali hech narsa yo'q)"

    prompt = f"""
Sen "{config.CHANNEL_BRAND}" nomli Telegram kanali uchun kontent tayyorlovchi yordamchisan.
Kanal yo'nalishi: {config.RUBRIKA}

Vazifa:
1. Claude AI (Anthropic)ning imkoniyatlari, foydalanish usullari yoki amaliy promptlash
   texnikalari haqida ANIQ va AMALIY bitta mavzu tanla. Mavzu quyidagi ro'yxatda
   allaqachon ishlatilganlardan FARQ QILISHI SHART:
{avoid_list}
2. Shu mavzu asosida Telegram posti yoz. Post o'zbek tilida bo'lishi kerak.

{config.POST_STYLE_GUIDE}

Javobni FAQAT quyidagi JSON formatida qaytar (boshqa hech qanday matn, izoh yoki markdown bo'lmasin):
{{
  "topic": "mavzuning qisqa nomi (5-8 so'z, tarixga yozib qo'yish uchun)",
  "post_text": "to'liq tayyor Telegram posti matni (emoji va hashtaglar bilan)",
  "image_prompt": "shu post uchun mos, qisqa inglizcha mavzu tavsifi (rasm uchun sarlavha sifatida ishlatiladi)",
  "audio_text": "postning audio o'qish uchun moslashtirilgan versiyasi - hashtag va emojilarsiz, tabiiy gapiriladigan uslubda, 400-700 belgi"
}}
"""
    raw_text = _chat(prompt)
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
    raw_text = _chat(prompt)
    return _parse_json_block(raw_text)
