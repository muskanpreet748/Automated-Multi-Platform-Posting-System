"""Discord integration — posts the message through a channel webhook.

How to get the credential:
    Discord -> Server Settings -> Integrations -> Webhooks -> New Webhook
    -> Copy Webhook URL  ->  paste into .env as DISCORD_WEBHOOK_URL

Docs: https://discord.com/developers/docs/resources/webhook
"""

import httpx

from app import config
from app.platforms.base import BasePlatform


class DiscordWebhook(BasePlatform):
    name = "Discord"

    def post(self, message: str):
        if not config.DISCORD_WEBHOOK_URL:
            return self.failure("DISCORD_WEBHOOK_URL is not set in .env")

        # ?wait=true makes Discord return the created message so we can
        # build a direct link to it.
        url = config.DISCORD_WEBHOOK_URL
        if "wait=" not in url:
            url = f"{url}{'&' if '?' in url else '?'}wait=true"

        try:
            response = httpx.post(
                url, json={"content": message}, timeout=self.timeout
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            return self.failure(f"Discord request failed: {exc}")

        # Discord sometimes answers with 204 (no body at all).
        if response.status_code == 204 or not response.content:
            return self.success(None)

        try:
            data = response.json()
        except ValueError:
            return self.success(None)

        message_id = data.get("id")
        channel_id = data.get("channel_id")
        guild_id = data.get("guild_id")

        posted_url = None
        if guild_id and channel_id and message_id:
            posted_url = (
                f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}"
            )
        return self.success(posted_url)
