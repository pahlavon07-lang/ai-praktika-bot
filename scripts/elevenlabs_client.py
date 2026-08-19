"""ElevenLabs API bilan matnni ovozga aylantirish (4-agent), so'ng Telegram
"ovozli xabar" (voice message) uchun kerakli OGG/OPUS formatiga o'giradi
(ffmpeg orqali - GitHub Actions ubuntu-latest'da tayyor o'rnatilgan)."""
import os
import subprocess
import tempfile

import requests

import config

BASE_URL = "https://api.elevenlabs.io/v1"


def _text_to_mp3(text: str) -> bytes:
    url = f"{BASE_URL}/text-to-speech/{config.ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": config.ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    body = {
        "text": text,
        "model_id": config.ELEVENLABS_MODEL_ID,
        "voice_settings": {
            "stability": 0.35,
            "similarity_boost": 0.8,
            "style": 0.6,
            "use_speaker_boost": True,
        },
    }
    resp = requests.post(url, headers=headers, json=body, params={"output_format": "mp3_44100_128"}, timeout=90)
    if resp.status_code != 200:
        raise RuntimeError(f"ElevenLabs API xatosi: HTTP {resp.status_code} - {resp.text[:800]}")
    return resp.content


def _mp3_to_ogg_opus(mp3_bytes: bytes) -> bytes:
    with tempfile.TemporaryDirectory() as tmp:
        mp3_path = os.path.join(tmp, "in.mp3")
        ogg_path = os.path.join(tmp, "out.ogg")
        with open(mp3_path, "wb") as f:
            f.write(mp3_bytes)
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", mp3_path, "-c:a", "libopus", "-b:a", "64k", "-ar", "48000", ogg_path],
            capture_output=True,
            timeout=60,
        )
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg xatosi: {result.stderr.decode(errors='ignore')[:800]}")
        with open(ogg_path, "rb") as f:
            return f.read()


def generate_voice_message(text: str) -> bytes:
    """To'liq oqim: matn -> ElevenLabs (mp3) -> ffmpeg (ogg/opus).
    Telegram sendVoice uchun tayyor bytes qaytaradi."""
    mp3_bytes = _text_to_mp3(text)
    return _mp3_to_ogg_opus(mp3_bytes)
