from typing import Optional

from pydantic import BaseModel


class ReviewPayload(BaseModel):
    review_id: str
    review_text: str


class ReviewResponse(BaseModel):
    status: str
    review_id: str
    message: str


class ReviewStatusResponse(BaseModel):
    review_id: str
    status: str
    sentiment: Optional[str] = None
    summary: Optional[str] = None
    processed_at: Optional[str] = None
    message: Optional[str] = None