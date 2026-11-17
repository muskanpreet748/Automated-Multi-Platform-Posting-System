"""Dev.to integration — creates a published article.

How to get the credential:
    dev.to -> Settings -> Extensions -> DEV Community API Keys
    -> Generate API Key -> paste into .env as DEVTO_API_KEY

Docs: https://developers.forem.com/api/v1 (Create a new article)
"""

import httpx

from app import config
from app.platforms.base import BasePlatform
from app.utils import title_from_message


class DevTo(BasePlatform):
    name = "Dev.to"

    def post(self, message: str):
        if not config.DEVTO_API_KEY:
            return self.failure("DEVTO_API_KEY is not set in .env")

        headers = {
            "api-key": config.DEVTO_API_KEY,
            "accept": "application/vnd.forem.api-v1+json",
            "content-type": "application/json",
        }
        payload = {
            "article": {
                "title": title_from_message(message),
                "body_markdown": message,
                "published": True,  # publish immediately instead of a draft
                "tags": ["automation", "api"],
            }
        }

        try:
            response = httpx.post(
                "https://dev.to/api/articles",
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
        except httpx.HTTPError as exc:
            return self.failure(f"Dev.to request failed: {exc}")

        if response.status_code not in (200, 201):
            return self.failure(self.error_text(response))

        return self.success(response.json().get("url"))
