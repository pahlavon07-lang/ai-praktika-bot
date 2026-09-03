"""Postlar uchun oldindan belgilangan mavzular ketma-ketligi (curriculum).

Har bir keyingi post shu ro'yxatdagi navbatdagi (hali ishlatilmagan) band bo'yicha
yoziladi - Gemini mavzuni o'zi tanlamaydi, faqat shu mavzu asosida post yozadi.
Ro'yxat to'liq tugagach (barcha bandlar used_topics ichida bo'lsa), tizim avtomatik
ravishda avvalgi "erkin tanlov" rejimiga qaytadi (generate_topic_and_post ichida).
"""

CURRICULUM = [
    "Claude Desktop ilovasi bilan tanishish: nima uchun kerak va qanday o'rnatiladi",
    "Claude Desktop sozlamalari (Settings): asosiy parametrlar va ularning vazifasi",
    "Claude Desktop'da loyihalar (Projects) bilan ishlash",
    "Claude Desktop'da fayl, rasm yoki PDF yuklab tahlil qildirish",
    "Claude Code - dasturlash uchun terminal/IDE integratsiyasi",
    "Artifacts - kod, hujjat yoki diagrammani alohida oynada ko'rish va tahrirlash",
    "Custom instructions - Claude'ga doimiy shaxsiy ko'rsatma berish",
    "Veb qidiruv (web search) orqali real vaqtdagi ma'lumot olish",
    "Ovozli rejim (voice mode) orqali Claude bilan gaplashib ishlash",
    "Prompt yozish texnikasi: aniq misollar (few-shot) berish",
    "Prompt yozish texnikasi: Claude'ga aniq rol va vazifa belgilash",
    "Claude mobil ilovasi (iOS/Android) imkoniyatlari",
    "Claude in Chrome - brauzerda sahifalarni ko'rish va boshqarish",
    "Uzun matnlarni qisqartirish va professional tahrirlash",
    "Jadval yoki statistik ma'lumotlarni tahlil qildirish",
]


def next_topic(used_topics: list[str]) -> str | None:
    """Ishlatilmagan navbatdagi curriculum mavzusini qaytaradi.
    Agar barchasi ishlatilgan bo'lsa - None (erkin tanlov rejimiga o'tish belgisi)."""
    for topic in CURRICULUM:
        if topic not in used_topics:
            return topic
    return None
