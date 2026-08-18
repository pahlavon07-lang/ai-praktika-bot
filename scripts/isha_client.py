"""Aisha AI API bilan o'zbek tilida tabiiy ovoz generatsiyasi (4-agent).
ElevenLabs'dan farqli o'laroq, bu xizmat aynan o'zbek tili uchun maxsus
o'qitilgan ("Gulnoza" modeli), shuning uchun talaffuz va ohang ancha
tabiiyroq chiqadi.
"""
import requests

import config

BASE_URL = "https://back.aisha.group"


def generate_audio(text: str) -> bytes:
    resp = requests.post(
        f"{BASE_URL}/api/v1/tts/post/",
        headers={"X-Api-Key": config.AISHA_API_KEY, "Accept-Language": "uz"},
        data={
            "transcript": text[:1000],
            "language": "uz",
            "model": "Gulnoza",
            "mood": config.AISHA_MOOD,
            "speed": 1.0,
        },
        timeout=90,
    )
    if resp.status_code not in (200, 201):
        raise RuntimeError(f"Aisha TTS API xatosi: HTTP {resp.status_code} - {resp.text[:800]}")
    data = resp.json()
    audio_path = data.get("audio_path")
    if not audio_path:
        raise RuntimeError(f"Aisha TTS javobida audio_path topilmadi: {data}")

    audio_resp = requests.get(f"{BASE_URL}{audio_path}", timeout=60)
    if audio_resp.status_code != 200:
        raise RuntimeError(f"Aisha audio faylini yuklab bo'lmadi: HTTP {audio_resp.status_code}")
    return audio_resp.content
