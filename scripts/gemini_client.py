"""Gemini API (generateContent) bilan matn generatsiyasi: mavzu+post yozish va
sifat nazorati (QC). Karta talab qilmaydi, matn generatsiyasi uchun kvota
muammosi yo'q (faqat rasm modellarida bor - shuning uchun rasm uchun
Pollinations ishlatiladi)."""
import json
import re

import requests

import config

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def _generate(prompt: str, timeout: int = 90) -> str:
    url = GEMINI_URL.format(model=config.GEMINI_TEXT_MODEL)
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": config.GEMINI_API_KEY,
    }
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    resp = requests.post(url, headers=headers, json=body, timeout=timeout)
    if resp.status_code != 200:
        raise RuntimeError(f"Gemini API xatosi ({config.GEMINI_TEXT_MODEL}): HTTP {resp.status_code} - {resp.text[:1200]}")
    data = resp.json()
    try:
        parts = data["candidates"][0]["content"]["parts"]
        text = "".join(p.get("text", "") for p in parts if "text" in p)
        if not text.strip():
            raise KeyError("bo'sh matn")
        return text.strip()
    except (KeyError, IndexError) as exc:
        raise RuntimeError(f"Gemini javobidan matn topilmadi: {json.dumps(data)[:1200]}") from exc


def _parse_json_block(raw_text: str) -> dict:
    cleaned = re.sub(r"^```(json)?|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()
    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if not match:
        raise RuntimeError(f"JSON topilmadi Gemini javobida: {raw_text[:1200]}")
    return json.loads(match.group(0))


def generate_topic_and_post(used_topics: list[str]) -> dict:
    """1 va 2-agent: mavzu tanlaydi va postni yozadi."""
    avoid_list = "\n".join(f"- {t}" for t in used_topics[-60:]) or "(hali hech narsa yo'q)"

    prompt = f"""
Sen "{config.CHANNEL_BRAND}" nomli Telegram kanali uchun kontent tayyorlovchi yordamchisan.
Kanal yo'nalishi: {config.RUBRIKA}

Vazifa:
1. Claude AI (Anthropic)ning imkoniyatlari, foydalanish usullari yoki amaliy promptlash
   texnikalari haqida ANIQ va AMALIY bitta mavzu tanla. Mavzu ANIQ bir funksiya, vosita
   yoki texnikaga asoslangan bo'lishi SHART (quyidagi ro'yxatdan ilhomlaning, lekin
   ularga qat'iy cheklanmang - boshqa amaliy mavzular ham bo'lishi mumkin):
   - Projects (loyihalar) - fayllarni saqlab, doimiy kontekst bilan ishlash
   - Artifacts - kod, hujjat, jadval, diagramma kabi natijalarni alohida oynada ko'rish/tahrirlash
   - Claude Code - dasturlash uchun terminal/IDE orqali ishlash
   - Fayl, rasm yoki PDF yuklab ulardan savol-javob qilish / tahlil qildirish
   - Veb qidiruv orqali real vaqtdagi, yangi ma'lumot olish
   - Ovozli rejim (voice mode) orqali gaplashib ishlash
   - Custom instructions / System prompt - Claude'ga doimiy shaxsiy ko'rsatma berish
   - Prompt yozish texnikalari: aniq misollar berish (few-shot), qat'iy format so'rash,
     bosqichma-bosqich fikrlashga undash, Claude'ga aniq rol/vazifa belgilash
   - Uzun matnlarni qisqartirish, tarjima qilish yoki professional tahrirlash
   - Jadval yoki statistik ma'lumotlarni tahlil qildirish
   - Ish xatlari, email, taqdimot yoki reklama matnlarini yozdirish/tuzatish
   - O'qish-o'rganishda yordamchi sifatida foydalanish (tushuntirish so'rash, test/mashq tuzdirish)
   - Ijodiy yozuv (hikoya, sarlavha, post g'oyalari, sarlavha variantlari)
   - Kodlashda xato topish va tuzatish (debugging), kodni tushuntirib berish
   - Claude Desktop ilovasi - kompyuterga o'rnatish, imkoniyatlari va sozlamalari
   - Claude mobil ilovasi (iOS/Android) - telefonda foydalanish
   - Claude in Chrome - brauzerda sahifalarni ko'rish, to'ldirish va boshqarish
   Mavzu quyidagi ro'yxatda allaqachon ishlatilganlardan FARQ QILISHI SHART:
{avoid_list}
2. Shu mavzu asosida Telegram posti yoz. Post o'zbek tilida bo'lishi kerak va albatta
   ANIQ AMALIY QIYMAT berishi SHART - o'quvchi postni o'qib bo'lgach, Claude'da ANIQ
   nimani va qanday qilib sinab ko'rishni bilib olishi kerak (quruq falsafiy/hissiy
   mulohaza emas, balki haqiqiy foydali maslahat).
3. ANIQLIK SHART: faqat ishonchli va tekshirilishi mumkin bo'lgan ma'lumot yoz. Aniq tugma
   nomi, menyu joylashuvi, narx yoki funksiya haqida ANIQ eslay olmasang - taxmin qilib,
   noto'g'ri yoki eskirgan ma'lumot o'ylab topma; buning o'rniga umumiyroq, lekin haqiqatga
   mos tavsif ber. Mavhum yoki isbotlanmagan da'volardan ("eng yaxshi", "hammasini biladi",
   "hech kim bilmaydi" kabi) qoch - faqat aniq, konkret va tekshirilishi mumkin bo'lgan
   gaplar yoz.

{config.POST_STYLE_GUIDE}

Javobni FAQAT quyidagi JSON formatida qaytar (boshqa hech qanday matn, izoh yoki markdown bo'lmasin):
{{
  "topic": "mavzuning qisqa nomi (5-8 so'z, tarixga yozib qo'yish uchun)",
  "post_text": "to'liq tayyor Telegram posti matni, POST_STYLE_GUIDE'ga qat'iy amal qilgan holda (faqat <b> va <em> teglar, emoji/hashtagsiz, qisqa fikrlar orasida bo'sh qator bilan)",
  "image_prompt": "shu post mavzusiga mos, INGLIZ TILIDA, qisqa (10-20 so'z) vizual tavsif - faqat NIMA tasvirlanishi kerakligini yoz (masalan 'a glowing brain made of circuits floating above an open book'), stil so'zlarini yozma - ular avtomatik qo'shiladi",
  "audio_text": "postning audio o'qish uchun moslashtirilgan versiyasi - HTML teglar, hashtag va emojilarsiz, tabiiy gapiriladigan uslubda, 300-600 belgi"
}}
"""
    raw_text = _generate(prompt)
    return _parse_json_block(raw_text)


def qc_check(post_text: str) -> dict:
    """5-agent: sifat nazorati. Qaytaradi {"ok": bool, "reason": str}."""
    prompt = f"""
Quyidagi Telegram post matnini sifat nazoratidan o'tkaz. Post "{config.CHANNEL_BRAND}" kanali uchun,
yo'nalishi: {config.RUBRIKA}

Tekshirish mezonlari:
- O'zbek tilida grammatik xatolarsiz yozilganmi?
- Claude AI'dan amaliy foydalanish bilan bog'liqmi?
- POSTDA KAMIDA BITTA ANIQ, NOMLANGAN Claude funksiyasi, vositasi yoki promptlash
  texnikasi tilga olinganmi va o'quvchiga ANIQ nima qilish kerakligi (amaliy qadam
  yoki misol) tushuntirilganmi? Agar post faqat umumiy falsafiy mulohaza, hissiy
  kuzatuv yoki "AI hayotimizni o'zgartiryapti" kabi quruq gap bo'lib, hech qanday
  ANIQ va sinab ko'rish mumkin bo'lgan foydali ma'lumot bermasa - buni RAD ETING
  (ok: false, reason: "quruq/umumiy gap, aniq amaliy qiymat yo'q").
- Uzunligi maqbulmi (300-1100 belgi oralig'ida)?
- Emoji yoki hashtag ISHLATILMAGANMI (bular bo'lmasligi SHART)?
- Faqat <b> va <em> teglaridan boshqa HTML teg ISHLATILMAGANMI?
- Soxta da'vo, reklama, siyosiy/diniy mazmun yo'qmi?

POST MATNI:
---
{post_text}
---

Javobni FAQAT JSON formatida qaytar: {{"ok": true yoki false, "reason": "qisqa asos (o'zbek tilida)"}}
"""
    raw_text = _generate(prompt)
    return _parse_json_block(raw_text)
