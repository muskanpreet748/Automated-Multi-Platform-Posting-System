"""Request and response models built with Pydantic.

Pydantic automatically validates the JSON that arrives at the API:
if the rules below are broken, FastAPI answers with HTTP 422 and a
clear error message — no extra code needed in the endpoint.
"""

from typing import List, Optional

from pydantic import BaseModel, field_validator

from app.utils import find_urls


class PostingRequest(BaseModel):
    """Body of POST /posting -> {"message": "..."}"""

    message: str

    @field_validator("message")
    @classmethod
    def message_must_be_valid(cls, value: str) -> str:
        text = value.strip()

        # Rule 1: not empty
        if not text:
            raise ValueError("Message must not be empty.")

        # Rule 2: maximum 200 characters
        if len(text) > 200:
            raise ValueError(
                f"Message must not exceed 200 characters (got {len(text)})."
            )

        # Rule 3: exactly one CTA link
        urls = find_urls(text)
        if len(urls) != 1:
            raise ValueError(
                f"Message must contain exactly one CTA link (found {len(urls)})."
            )

        # Rule 4: the link must be a valid http(s) URL with a real domain
        from urllib.parse import urlparse

        parsed = urlparse(urls[0])
        if (
            parsed.scheme not in ("http", "https")
            or not parsed.netloc
            or "." not in parsed.netloc
        ):
            raise ValueError(f"'{urls[0]}' is not a valid URL.")

        return text


class PlatformResult(BaseModel):
    """One row of the posting report (one per platform)."""

    platform: str
    status: str  # "success" | "failed"
    posted_url: Optional[str] = None
    public_access: bool = False
    date: Optional[str] = None
    time: Optional[str] = None
    error: Optional[str] = None


class PostingResponse(BaseModel):
    """Full response of POST /posting."""

    success: bool
    results: List[PlatformResult]
