"""Registry of all platforms the application can post to.

Adding a new platform = create one file in this folder and add the
class to get_platforms(). Nothing else has to change.
"""

from app.platforms.base import BasePlatform
from app.platforms.devto import DevTo
from app.platforms.discord_webhook import DiscordWebhook
from app.platforms.hashnode import Hashnode
from app.platforms.mastodon import Mastodon
from app.platforms.pastebin import Pastebin
from app.platforms.telegram_bot import TelegramBot


def get_platforms() -> list:
    """Return one fresh instance of every supported platform."""
    return [
        DiscordWebhook(),
        TelegramBot(),
        DevTo(),
        Mastodon(),
        Hashnode(),
        Pastebin(),
    ]


__all__ = ["BasePlatform", "get_platforms"]
