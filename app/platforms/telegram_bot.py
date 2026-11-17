"""Telegram integration — sends the message with a Telegram bot.

How to get the credentials:
    1. Message @BotFather on Telegram -> /newbot -> copy the token.
    2. Add the bot to your channel or group and send it one message.
    3. Find the chat id (e.g. @userinfobot) -> TELEGRAM_CHAT_ID.
       Use "@yourchannel" for public channels so we can build a link.

Docs: https://core.telegram.org/bots/api#sendmessage
"""

import httpx

from app import config
from app.platforms.base import BasePlatform


class TelegramBot(BasePlatform):
    name = "Telegram"

    def post(self, message: str):
        if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
            return self.failure(
                "TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID are not set in .env"
            )

        api_url = (
            f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
        )
        payload = {
            "chat_id": config.TELEGRAM_CHAT_ID,
            "text": message,
        }

        try:
            response = httpx.post(api_url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as exc:
            return self.failure(f"Telegram request failed: {exc}")
        except ValueError:
            return self.failure("Telegram returned an invalid response")

        if not data.get("ok"):
            return self.failure(str(data.get("description", "Unknown Telegram error")))

        # Public channels (@username) can be linked to directly.
        chat_id = config.TELEGRAM_CHAT_ID
        is_public = chat_id.startswith("@")
        posted_url = None
        if is_public:
            message_id = data.get("result", {}).get("message_id")
            if message_id:
                posted_url = f"https://t.me/{chat_id[1:]}/{message_id}"

        return self.success(posted_url, public_access=is_public)
