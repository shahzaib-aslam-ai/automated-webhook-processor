import os
import json
import logging

from fastapi import (
    FastAPI,
    BackgroundTasks,
    Request,
    Header,
    HTTPException
)

from dotenv import load_dotenv

from models import (
    ReviewPayload,
    ReviewResponse,
    ReviewStatusResponse
)

from security import verify_signature

from services import (
    process_review_background
)

from middleware import request_logging_middleware

load_dotenv()

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

app = FastAPI(
    title="Webhook Review Processor"
)

app.middleware("http")(
    request_logging_middleware
)

@app.post(
    "/webhook/process-review",
    response_model=ReviewResponse
)
async def receive_webhook(
    request: Request,
    payload: ReviewPayload,
    background_tasks: BackgroundTasks,
    x_webhook_signature: str = Header(...)
):
    
    review_id = payload.review_id

    logging.info(
        f"Webhook received: review_id={review_id}"
    )

    file_path = f"processed/{review_id}.json"

    if os.path.exists(file_path):

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            existing_data = json.load(file)

        if existing_data.get("status") == "processing":

            return {
                "status": "already_processing",
                "review_id": review_id,
                "message": "This review is already being processed."
            }

        return {
            "status": "already_processed",
            "review_id": review_id,
            "message": "This review has already been processed."
        }

    payload_body = await request.body()

    is_valid = verify_signature(
        payload_body,
        x_webhook_signature
    )

    if not is_valid:

        raise HTTPException(
            status_code=401,
            detail="Invalid webhook signature"
        )

    cleaned_text = " ".join(
        payload.review_text.strip().split()
    )

    processing_data = {
        "review_id": review_id,
        "status": "processing"
    }

    os.makedirs(
        "processed",
        exist_ok=True
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            processing_data,
            file,
            indent=4
        )

    background_tasks.add_task(
        process_review_background,
        review_id,
        cleaned_text
    )

    return {
        "status": "received",
        "review_id": review_id,
        "message": "Processing started. Check status endpoint for result."
    }

@app.get(
    "/webhook/status/{review_id}",
    response_model=ReviewStatusResponse
)
async def get_review_status(
    review_id: str
):

    file_path = f"processed/{review_id}.json"

    if not os.path.exists(file_path):

        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return data