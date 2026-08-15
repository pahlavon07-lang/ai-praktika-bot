# AI Praktika by KR — avtomatik post pipeline

Bu repo har kuni **09:00, 13:00 va 18:00 (Toshkent vaqti)** da Telegram kanalga
avtomatik post chiqaradigan tizimni ishga tushiradi. Har bir post: mavzu
izlash → matn yozish → rasm generatsiya (Gemini/Nano Banana) → audio
generatsiya (ElevenLabs) → sifat nazorati → sizga preview (tasdiqlash oynasi
bilan) → kanalga chiqarish bosqichlaridan o'tadi.

## 1. Sozlash (bir martalik)

### A) Repo yaratish
1. GitHub'da yangi **private** repository yarating (masalan `ai-praktika-bot`).
2. Ushbu papkadagi barcha fayllarni (`.github/`, `scripts/`, `data/`,
   `requirements.txt`, `README.md`) shu repoga yuklang — eng oson yo'li:
   GitHub sahifasida "Add file" → "Upload files" → barcha fayl/papkalarni
   torting-tashlang → "Commit changes".

### B) Secrets qo'shish (maxfiy kalitlar)
Repo sahifasida: **Settings → Secrets and variables → Actions → Secrets**
tab → **New repository secret**. Quyidagi 3 tasini qo'shing:

| Nomi | Qiymati |
|---|---|
| `TELEGRAM_BOT_TOKEN` | BotFather bergan token |
| `GEMINI_API_KEY` | Google AI Studio'dan olingan kalit |
| `ELEVENLABS_API_KEY` | ElevenLabs'dan olingan kalit |

### C) Variables qo'shish (maxfiy bo'lmagan sozlamalar)
Xuddi shu sahifada **Variables** tab → **New repository variable**:

| Nomi | Qiymati | Izoh |
|---|---|---|
| `CHANNEL_USERNAME` | `@ai_praktika` (yoki yaratgan username'ingiz) | boshida @ bilan |
| `ADMIN_CHAT_ID` | sizning shaxsiy Telegram raqamli ID'ingiz | pastga qarang, qanday olishni |

Ixtiyoriy (agar qo'shmasangiz, kod ichidagi standart qiymat ishlatiladi):
`ELEVENLABS_VOICE_ID`, `ELEVENLABS_MODEL_ID`, `GEMINI_TEXT_MODEL`,
`GEMINI_IMAGE_MODEL`, `WAIT_MINUTES`.

**ADMIN_CHAT_ID qanday olinadi:**
1. Telegram'da yaratgan botingizga (masalan `@ai_praktika_bot`) `/start` yozing.
2. Keyin Telegram'da `@userinfobot` ni toping, unga istalgan xabar yozing —
   u sizga "Id: 123456789" tarzida raqam qaytaradi. Shu raqamni
   `ADMIN_CHAT_ID` sifatida qo'ying.

### D) Birinchi test
1. Repo sahifasida **Actions** tab → chap tomonda "AI Praktika - avtomatik
   post" workflow'ni tanlang → o'ng tomonda **Run workflow** tugmasini bosing.
2. Bir necha daqiqadan so'ng botdan sizning shaxsiy chatingizga post preview'i
   (rasm + matn + audio + tugmalar) kelishi kerak.
3. Agar xato chiqsa — Actions sahifasidagi ishlagan run'ni oching, qizil
   bosqichni bosing, xato matnini menga (shu suhbatga) tashlang — men kodni
   tuzataman.

## 2. Kundalik ishlash tartibi

Har bir jadval vaqtidan 10 daqiqa oldin sizga preview keladi:
- Hech narsa bosmasangiz → 10 daqiqadan so'ng post avtomatik kanalga chiqadi.
- **"🔄 Qayta qilish"** bossangiz → butun post (mavzu, matn, rasm, audio)
  qaytadan tayyorlanadi va tayyor bo'lishi bilan (jadval vaqtidan kech qolsa
  ham) kanalga chiqariladi.
- **"✅ Hoziroq chiqarish"** bossangiz → kutmasdan darhol kanalga chiqadi.

Istalgan boshqa vaqtda qo'lda post qo'yish uchun: **Actions → Run workflow**
tugmasini bosing — xuddi shu oqim (preview + 9 daqiqa kutish) ishga tushadi.

## 3. Muammo yuzaga kelsa

- **"model topilmadi" (404) xatosi**: Google/ElevenLabs vaqti-vaqti bilan
  model nomlarini yangilaydi. `GEMINI_TEXT_MODEL` yoki `GEMINI_IMAGE_MODEL`
  variable'ini joriy nomga yangilang (aniq nomni
  https://ai.google.dev/gemini-api/docs sahifasidan tekshiring).
- **Bot preview yubormayapti**: `ADMIN_CHAT_ID` to'g'ri ekanini va botga
  `/start` yozganingizni tekshiring.
- **Kanalga chiqmayapti**: bot kanalga admin qilib qo'shilganini va
  "Post Messages" huquqi yoqilganini tekshiring.
