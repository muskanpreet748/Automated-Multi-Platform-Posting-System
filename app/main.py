"""FastAPI entry point — run it with:

    uvicorn app.main:app --host 0.0.0.0 --port 4000

Interactive documentation: http://localhost:4000/docs
"""

from fastapi import FastAPI

from app.schemas import PostingRequest, PostingResponse
from app.services.posting_service import post_to_all

app = FastAPI(
    title="Automated Multi-Platform Posting System",
    description=(
        "Publishes a short message (max 200 characters with exactly one "
        "CTA link) to multiple third-party platforms."
    ),
    version="1.0.0",
)


@app.get("/")
def health_check():
    """Simple health check so you can see the server is alive."""
    return {"status": "ok", "docs": "http://localhost:4000/docs"}


@app.post("/posting", response_model=PostingResponse, tags=["posting"])
def posting(payload: PostingRequest) -> PostingResponse:
    """Validate the message, then publish it to every configured platform.

    One platform failing never stops the others — every platform runs
    inside its own try/except inside the posting service.
    """
    return post_to_all(payload.message)
