"""Telegram Bot API bilan ishlash: admin'ga preview yuborish, tugma bosilishini
kuzatish (polling) va kanalga chiqarish (6-agent)."""
import json
import time
import requests
import config

API_BASE = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}"

BTN_REDO = "redo"
BTN_PUBLISH_NOW = "publish_now"


def _call(method: str, data: dict | None = None, files: dict | None = None, timeout: int = 30) -> dict:
    url = f"{API_BASE}/{method}"
    resp = requests.post(url, data=data or {}, files=files, timeout=timeout)
    payload = resp.json()
    if not payload.get("ok"):
        raise RuntimeError(f"Telegram API xatosi ({method}): {payload}")
    return payload["result"]


def _split_caption(text: str, limit: int = 1024) -> tuple[str, str]:
    if len(text) <= limit:
        return text, ""
    cut = text.rfind("\n", 0, limit)
    if cut == -1:
        cut = limit
    return text[:cut].strip(), text[cut:].strip()


def send_preview(post_text: str, image_bytes: bytes, audio_bytes: bytes) -> dict:
    """Adminga (shaxsiy chatga) tayyor postni + boshqaruv tugmalarini yuboradi.
    Qaytaradi: {"photo_message_id", "control_message_id", "photo_file_id", "audio_file_id"}
    """
    caption, rest = _split_caption(post_text)
    photo_result = _call(
        "sendPhoto",
        data={"chat_id": config.ADMIN_CHAT_ID, "caption": caption},
        files={"photo": ("post.png", image_bytes, "image/png")},
    )
    if rest:
        _call("sendMessage", data={"chat_id": config.ADMIN_CHAT_ID, "text": rest})

    audio_result = _call(
        "sendAudio",
        data={"chat_id": config.ADMIN_CHAT_ID, "title": config.CHANNEL_BRAND},
        files={"audio": ("post.mp3", audio_bytes, "audio/mpeg")},
    )

    keyboard = {
        "inline_keyboard": [[
            {"text": "\U0001F504 Qayta qilish", "callback_data": BTN_REDO},
            {"text": "✅ Hoziroq chiqarish", "callback_data": BTN_PUBLISH_NOW},
        ]]
    }
    control = _call(
        "sendMessage",
        data={
            "chat_id": config.ADMIN_CHAT_ID,
            "text": (
                f"Yuqoridagi post {config.WAIT_MINUTES:.0f} daqiqadan so'ng "
                f"{config.CHANNEL_USERNAME} kanaliga avtomatik chiqadi.\n"
                f"Agar o'zgartirish kerak bo'lsa - \"Qayta qilish\" tugmasini bosing.\n"
                f"Darhol chiqarish uchun - \"Hoziroq chiqarish\" tugmasini bosing."
            ),
            "reply_markup": json.dumps(keyboard),
        },
    )
    return {
        "control_message_id": control["message_id"],
        "photo_file_id": photo_result["photo"][-1]["file_id"],
        "audio_file_id": audio_result["audio"]["file_id"],
    }


def poll_for_decision(control_message_id: int, wait_minutes: float) -> str | None:
    """control_message_id ostidagi tugma bosilishini kutadi. Bosilsa BTN_REDO yoki
    BTN_PUBLISH_NOW qaytaradi, vaqt tugasa None qaytaradi."""
    deadline = time.time() + wait_minutes * 60
    offset = None
    # Eski update'larni tashlab yuborish uchun boshlang'ich offsetni olib qo'yamiz.
    initial = _call("getUpdates", data={"timeout": 0})
    if initial:
        offset = initial[-1]["update_id"] + 1

    while time.time() < deadline:
        remaining = max(1, int(deadline - time.time()))
        poll_timeout = min(25, remaining)
        params = {"timeout": poll_timeout}
        if offset is not None:
            params["offset"] = offset
        updates = _call("getUpdates", data=params, timeout=poll_timeout + 10)
        for update in updates:
            offset = update["update_id"] + 1
            cq = update.get("callback_query")
            if not cq:
                continue
            if cq.get("message", {}).get("message_id") != control_message_id:
                continue
            data = cq.get("data")
            _call("answerCallbackQuery", data={"callback_query_id": cq["id"], "text": "Qabul qilindi"})
            if data in (BTN_REDO, BTN_PUBLISH_NOW):
                return data
    return None


def publish_to_channel(post_text: str, photo_file_id: str, audio_file_id: str) -> None:
    caption, rest = _split_caption(post_text)
    _call("sendPhoto", data={"chat_id": config.CHANNEL_USERNAME, "photo": photo_file_id, "caption": caption})
    if rest:
        _call("sendMessage", data={"chat_id": config.CHANNEL_USERNAME, "text": rest})
    _call("sendAudio", data={"chat_id": config.CHANNEL_USERNAME, "audio": audio_file_id, "title": config.CHANNEL_BRAND})


def notify_admin(text: str) -> None:
    _call("sendMessage", data={"chat_id": config.ADMIN_CHAT_ID, "text": text})
