"""Pastebin integration — creates a public paste of the message.

How to get the credential:
    https://pastebin.com/doc_api -> "Generate your API key"
    -> paste into .env as PASTEBIN_API_KEY

Docs: https://pastebin.com/doc_api (api_post.php)
"""

import httpx

from app import config
from app.platforms.base import BasePlatform
from app.utils import title_from_message


class Pastebin(BasePlatform):
    name = "Pastebin"

    def post(self, message: str):
        if not config.PASTEBIN_API_KEY:
            return self.failure("PASTEBIN_API_KEY is not set in .env")

        payload = {
            "api_dev_key": config.PASTEBIN_API_KEY,
            "api_option": "paste",
            "api_paste_code": message,
            "api_paste_name": title_from_message(message),
            "api_paste_private": "0",  # public paste
            "api_paste_expire_date": "N",  # never expires
        }

        try:
            response = httpx.post(
                "https://pastebin.com/api/api_post.php",
                data=payload,
                timeout=self.timeout,
            )
        except httpx.HTTPError as exc:
            return self.failure(f"Pastebin request failed: {exc}")

        body = (response.text or "").strip()

        # On success Pastebin returns the URL as plain text; on failure
        # it returns an error string such as "Bad API request, ...".
        if response.status_code == 200 and body.startswith("http"):
            return self.success(body)

        return self.failure(body or self.error_text(response))
