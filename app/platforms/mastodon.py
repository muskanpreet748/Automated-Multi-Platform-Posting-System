"""Mastodon integration — publishes a public status.

How to get the credentials:
    Your Mastodon instance (e.g. mastodon.social)
    -> Preferences -> Development -> New Application
    -> copy the Access Token -> .env as MASTODON_ACCESS_TOKEN
    Also set MASTODON_API_BASE to your instance URL.

Docs: https://docs.joinmastodon.org/methods/statuses/#create
"""

import httpx

from app import config
from app.platforms.base import BasePlatform


class Mastodon(BasePlatform):
    name = "Mastodon"

    def post(self, message: str):
        if not config.MASTODON_ACCESS_TOKEN:
            return self.failure("MASTODON_ACCESS_TOKEN is not set in .env")

        url = f"{config.MASTODON_API_BASE}/api/v1/statuses"
        headers = {"Authorization": f"Bearer {config.MASTODON_ACCESS_TOKEN}"}
        payload = {"status": message, "visibility": "public"}

        try:
            response = httpx.post(
                url, headers=headers, json=payload, timeout=self.timeout
            )
        except httpx.HTTPError as exc:
            return self.failure(f"Mastodon request failed: {exc}")

        if response.status_code not in (200, 201):
            return self.failure(self.error_text(response))

        data = response.json()
        # The API answers with the public URL of the new status.
        return self.success(data.get("url"))
