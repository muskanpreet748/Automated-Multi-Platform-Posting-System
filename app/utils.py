"""Small shared helpers used by validation and the platform modules."""

import re

# Finds things like https://example.com inside a message.
URL_PATTERN = re.compile(r"https?://[^\s<>\"']+")


def find_urls(text: str) -> list:
    """Return every URL found in `text` (trailing punctuation removed)."""
    return [url.rstrip(".,;:!?)") for url in URL_PATTERN.findall(text)]


def title_from_message(message: str) -> str:
    """Build a short title for platforms that need one (Dev.to, Hashnode, Pastebin).

    We remove the link, collapse line breaks and keep at most 60 characters.
    """
    text = URL_PATTERN.sub("", message)
    text = " ".join(text.split()).strip()
    if len(text) > 60:
        text = text[:57].rstrip() + "..."
    return text or "Automated post"
