"""ElevenLabs API bilan matnni ovozga aylantirish (4-agent)."""
import requests

import config

BASE_URL = "https://api.elevenlabs.io/v1"


def generate_audio(text: str) -> bytes:
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
