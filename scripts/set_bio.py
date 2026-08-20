"""Bir martalik utility skript: Telegram kanal tavsifini (bio) Bot API orqali
yangilaydi. TELEGRAM_BOT_TOKEN qiymatini hech qachon logga yoki ekranga
chiqarmaydi - faqat HTTP status va Telegram javobini ko'rsatadi."""
import os

import requests

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL = os.environ.get("CHANNEL_USERNAME", "@ai_praktika_kr")

DESCRIPTION = (
    "Claude AI (sun'iy intellekt)dan ish, o'qish va biznesda amaliy foydalanish "
    "bo'yicha kundalik maslahatlar. Har kuni yangi texnika, funksiya va "
    "promptlash usullari - matn, rasm va ovozli formatda."
)


def main() -> None:
    url = f"https://api.telegram.org/bot{TOKEN}/setChatDescription"
    resp = requests.post(url, json={"chat_id": CHANNEL, "description": DESCRIPTION}, timeout=30)
    print(f"HTTP {resp.status_code}")
    data = resp.json()
    print(f"ok={data.get('ok')} description={data.get('description')}")
    resp.raise_for_status()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram xatosi: {data}")
    print("Kanal tavsifi muvaffaqiyatli yangilandi.")


if __name__ == "__main__":
    main()
