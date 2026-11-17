"""Reads all credentials from the .env file.

Environment variables keep secret API keys out of the source code,
so the repository can safely be made public on GitHub.
"""

import os

from dotenv import load_dotenv

# Loads the variables from the .env file into the process environment.
load_dotenv()


def get_setting(name: str, default: str = "") -> str:
    """Read one setting from the environment (empty string if missing)."""
    return os.getenv(name, default).strip()


# --- Discord ---------------------------------------------------
DISCORD_WEBHOOK_URL = get_setting("DISCORD_WEBHOOK_URL")

# --- Telegram --------------------------------------------------
TELEGRAM_BOT_TOKEN = get_setting("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = get_setting("TELEGRAM_CHAT_ID")

# --- Dev.to ----------------------------------------------------
DEVTO_API_KEY = get_setting("DEVTO_API_KEY")

# --- Mastodon --------------------------------------------------
MASTODON_API_BASE = get_setting("MASTODON_API_BASE", "https://mastodon.social").rstrip("/")
MASTODON_ACCESS_TOKEN = get_setting("MASTODON_ACCESS_TOKEN")

# --- Hashnode --------------------------------------------------
HASHNODE_PAT = get_setting("HASHNODE_PAT")
HASHNODE_PUBLICATION_ID = get_setting("HASHNODE_PUBLICATION_ID")

# --- Pastebin --------------------------------------------------
PASTEBIN_API_KEY = get_setting("PASTEBIN_API_KEY")
