"""Pollinations.ai orqali BEPUL, API kalitisiz, maksimal detallashgan
3D-render uslubidagi rasm generatsiyasi (3-agent)."""
import urllib.parse

import requests

import config

BASE_URL = "https://image.pollinations.ai/prompt"


def generate_image(prompt: str, seed: int = 1) -> bytes:
    full_prompt = f"{prompt}, {config.IMAGE_STYLE_SUFFIX}"
    encoded = urllib.parse.quote(full_prompt)
    url = f"{BASE_URL}/{encoded}"
    params = {
        "width": 1024,
        "height": 1024,
        "nologo": "true",
        "seed": seed,
        "model": "flux",
    }
    resp = requests.get(url, params=params, timeout=120)
    if resp.status_code != 200 or not resp.content:
        raise RuntimeError(f"Pollinations rasm xatosi: HTTP {resp.status_code} - {resp.text[:400]}")
    return resp.content
