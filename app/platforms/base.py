"""Common base class shared by every platform module.

Each platform only implements post(message); the success() and
failure() helpers build the standard result dictionary so that all
platforms return exactly the same shape of data.
"""

from datetime import datetime
from typing import Any, Dict, Optional


class BasePlatform:
    # Human readable name shown in the API response.
    name: str = "base"
    # Is the posted content readable by anyone without logging in?
    public_access: bool = True
    # Seconds we wait for the other platform to answer.
    timeout: float = 15.0

    def post(self, message: str) -> Dict[str, Any]:
        """Publish `message`. Must be implemented by every platform."""
        raise NotImplementedError("Every platform must implement post().")

    # ------------------------------------------------------------------
    def success(
        self, posted_url: Optional[str], public_access: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Standard 'success' result with the current date and time."""
        now = datetime.now()
        return {
            "platform": self.name,
            "status": "success",
            "posted_url": posted_url,
            "public_access": self.public_access if public_access is None else public_access,
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "error": None,
        }

    def failure(self, error: str) -> Dict[str, Any]:
        """Standard 'failed' result carrying the error details."""
        return {
            "platform": self.name,
            "status": "failed",
            "posted_url": None,
            "public_access": False,
            "date": None,
            "time": None,
            "error": error,
        }

    @staticmethod
    def error_text(response: Any) -> str:
        """Turn an HTTP error response into a short readable message."""
        body = (response.text or "").strip()
        if len(body) > 200:
            body = body[:200] + "..."
        return f"HTTP {response.status_code}: {body}" if body else f"HTTP {response.status_code}"
