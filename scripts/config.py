"""
Markazlashtirilgan konfiguratsiya. Barcha maxfiy va sozlanadigan qiymatlar
GitHub Actions muhit o'zgaruvchilaridan (Secrets/Variables) olinadi.

MUHIM: quyidagi model nomlari (GEMINI_TEXT_MODEL, GEMINI_IMAGE_MODEL) vaqti-vaqti
bilan Google tomonidan yangilanishi mumkin. Agar skript "model topilmadi" (404)
xatosi bersa, https://ai.google.dev/gemini-api/docs saytidan joriy model nomini
tekshirib, GitHub repo -> Settings -> Secrets and variables -> Actions -> Variables
bo'limida GEMINI_TEXT_MODEL / GEMINI_IMAGE_MODEL qiymatini yangilang (kodni
o'zgartirish shart emas).
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
CHANNEL_USERNAME = _env("CHANNEL_USERNAME")  # masalan "@ai_praktika"
ADMIN_CHAT_ID = _env("ADMIN_CHAT_ID")  # sizning shaxsiy Telegram ID raqamingiz

ELEVENLABS_VOICE_ID = _env("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # "Rachel" - standart
ELEVENLABS_MODEL_ID = _env("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")

GEMINI_TEXT_MODEL = _env("GEMINI_TEXT_MODEL", "gemini-2.5-flash")
GEMINI_IMAGE_MODEL = _env("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")

WAIT_MINUTES = float(_env("WAIT_MINUTES", "9"))
MAX_REGENERATE_ATTEMPTS = int(_env("MAX_REGENERATE_ATTEMPTS", "3"))

RUBRIKA = "Claude (sun'iy intellekt) dan kundalik ish, o'qish va biznesda foydalanish bo'yicha amaliy maslahatlar"

CHANNEL_BRAND = "AI Praktika by KR"

POST_STYLE_GUIDE = """
Post uslubi va formati (o'zbek tilida yoziladi):
1) Birinchi qatorda diqqat tortuvchi emoji + qisqa sarlavha (masalan: "\U0001F4A1 Claude'dan shu tarzda so'rasangiz...").
2) 2-4 ta qisqa paragraf yoki qisqa amaliy fikrlar bilan: aniq bitta maslahat, nega foydali ekani, va uni qanday qo'llash mumkinligi (agar mos bo'lsa, aniq misol yoki tayyor prompt namunasi bilan).
3) Oxirida qisqa chaqiriq (masalan: "Sinab ko'ring va natijani izohlarda yozing \U0001F447" yoki shunga o'xshash).
4) Postning oxirida 3-5 ta tegishli hashtag, masalan: #ClaudeAI #SuniyIntellekt #AIPraktika #Maslahat
5) Umumiy uzunlik: 600-1100 belgi atrofida (juda uzun bo'lmasin, Telegram'da o'qilishi qulay bo'lsin).
6) Ton: do'stona, professional, lekin murakkab bo'lmagan tilda - texnik jargon minimal.
7) Hech qanday soxta/tekshirilmagan da'vo, hech qanday reklama boshqa mahsulotga, hech qanday siyosiy/diniy mavzu bo'lmasin.
"""
