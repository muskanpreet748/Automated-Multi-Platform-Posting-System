"""Service layer — posts the message to every platform and builds the report.

Key design rule from the assignment:
    "Handle each platform independently. If one platform fails,
     continue posting to the remaining platforms."

That is why every platform call sits inside its own try/except.
"""

from typing import Any, Dict, List

from app.platforms import get_platforms


def _unexpected_failure(platform_name: str, error: Exception) -> Dict[str, Any]:
    """Failure row for a platform that crashed with an unexpected error.

    Built here (not by the platform) so that ANY object used as a
    platform can be reported safely.
    """
    return {
        "platform": platform_name,
        "status": "failed",
        "posted_url": None,
        "public_access": False,
        "date": None,
        "time": None,
        "error": f"Unexpected error: {error}",
    }


def post_to_all(message: str) -> Dict[str, Any]:
    """Publish `message` everywhere and return {success, results}."""
    results: List[Dict[str, Any]] = []

    for platform in get_platforms():
        try:
            results.append(platform.post(message))
        except Exception as exc:  # noqa: BLE001 - one platform must never break the rest
            # Even an unexpected programming error becomes a normal
            # "failed" row so the other platforms still run.
            results.append(_unexpected_failure(platform.name, exc))

    # The whole request counts as successful if at least one platform
    # accepted the message.
    any_success = any(result["status"] == "success" for result in results)

    return {"success": any_success, "results": results}
