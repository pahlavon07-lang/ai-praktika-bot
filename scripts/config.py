"""
Markazlashtirilgan konfiguratsiya. Barcha maxfiy va sozlanadigan qiymatlar
GitHub Actions muhit o'zgaruvchilaridan (Secrets/Variables) olinadi.
"""
import os


def _env(name: str, default: str = "") -> str:
    # GitHub Actions "vars.XXX" o'rnatilmagan bo'lsa ham, muhit o'zgaruvchisini
    # BO'SH QATOR sifatida beradi (umuman yo'q qilib emas) - shuning uchun
    # bo'sh qatorni ham "standart qiymatni qo'llash kerak" deb hisoblaymiz.
    value = os.environ.get(name, "").strip()
    return value if value else default


# --- Maxfiy kalitlar (Secrets) ---
TELEGRAM_BOT_TOKEN = _env("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = _env("GEMINI_API_KEY")
ELEVENLABS_API_KEY = _env("ELEVENLABS_API_KEY")

# --- Sozlamalar (Variables) ---
CHANNEL_USERNAME = _env("CHANNEL_USERNAME")  # masalan "@ai_praktika_kr"
ADMIN_CHAT_ID = _env("ADMIN_CHAT_ID")  # sizning shaxsiy Telegram ID raqamingiz

GEMINI_TEXT_MODEL = _env("GEMINI_TEXT_MODEL", "gemini-3.6-flash")

ELEVENLABS_VOICE_ID = _env("ELEVENLABS_VOICE_ID", "ydg3V9rJxFWplQkz1YYY")  # shaxsiy "AI прк" ovozi (bepul, Voice Design orqali yaratilgan)
ELEVENLABS_MODEL_ID = _env("ELEVENLABS_MODEL_ID", "eleven_v3")

WAIT_MINUTES = float(_env("WAIT_MINUTES", "9"))
MAX_REGENERATE_ATTEMPTS = int(_env("MAX_REGENERATE_ATTEMPTS", "2"))

RUBRIKA = "Claude (sun'iy intellekt) dan kundalik ish, o'qish va biznesda foydalanish bo'yicha amaliy maslahatlar"

CHANNEL_BRAND = "AI Praktika by KR"

# Uslub - foydalanuvchi bergan namuna kanal (Aziz Rahimov) yozish uslubidan
# ko'chirib olindi: aforistik, qisqa fikrlar, emojisiz, hashtagsiz, shaxsiy
# kuzatuv orqali umumiy xulosaga olib boradigan post.
POST_STYLE_GUIDE = """
Post uslubi va formati (o'zbek tilida yoziladi, namuna kanal uslubidan olingan):

1) HECH QANDAY emoji ishlatilmaydi. HECH QANDAY hashtag ishlatilmaydi.
2) Post to'g'ridan-to'g'ri fikr, kuzatuv yoki savol bilan boshlanadi - sarlavha yoki "salom" kabi kirish so'zlarisiz.
3) Matn juda qisqa fikrlardan/jumlalardan iborat bo'ladi - HAR BIR fikr alohida qatorda, orasida BO'SH QATOR bilan (ya'ni ikkita \\n\\n) ajratiladi. Bu aforistik, "nafas oladigan" ritm beradi.
4) Uslub: odatda shaxsiy kuzatuv yoki tajriba orqali boshlanadi ("Ko'rdim...", "Sinab ko'rdim...", "O'ylab qoldim..." kabi), so'ng shundan Claude AI bilan bog'liq amaliy xulosaga olib keladi.
5) Ba'zan raqamlangan fikrlar bo'lishi mumkin (1-, 2-, 3- kabi), lekin bullet-list emas, oddiy oqim ichida yoziladi.
6) Takrorlanuvchi parallel tuzilishlar ishlatish mumkin (masalan "Ba'zilar... Ba'zilar... Ba'zilar..." kabi) - kuchli ritm uchun.
7) Post OXIRI kuchli, esda qolarli, qisqa bitta jumla/aforizm bilan tugaydi - shu yakuniy jumlani <b>...</b> HTML tegi bilan qalin qilib belgilang.
8) Iqtibos yoki alohida urg'u berilishi kerak bo'lgan so'z/jumlalar uchun <em>...</em> (kursiv) ishlatilishi mumkin.
9) Mavzu doim Claude AI (sun'iy intellekt)dan amaliy foydalanish bilan bog'liq bo'lishi kerak - lekin quruq "qanday qilish" ro'yxati emas, balki hikoya yoki kuzatuv orqali yetkaziladi.
10) Umumiy uzunlik: 400-900 belgi atrofida.
11) Matn ichida FAQAT <b> va <em> HTML teglaridan foydalaning, boshqa hech qanday teg ishlatmang (ular Telegram'da to'g'ridan-to'g'ri qalin/kursiv qilib ko'rsatiladi).
12) Hech qanday soxta/tekshirilmagan da'vo, hech qanday reklama boshqa mahsulotga, hech qanday siyosiy/diniy mavzu bo'lmasin.
"""

# 3D-render uslubidagi rasm uchun umumiy stil so'zlari (Pollinations.ai promptiga qo'shiladi)
IMAGE_STYLE_SUFFIX = (
    "highly detailed 3D render, octane render, cinema4d style, studio lighting, "
    "vibrant colors, professional illustration, ultra detailed, 4k, no text, no watermark, no words"
)
