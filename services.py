import os
import json
import logging
from datetime import datetime

from dotenv import load_dotenv
from groq import AsyncGroq


load_dotenv()


logger = logging.getLogger(__name__)

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError("GROQ_API_KEY is missing")


client = AsyncGroq(api_key=api_key)


def save_result(review_id: str, result: dict):

    os.makedirs("processed", exist_ok=True)

    file_path = f"processed/{review_id}.json"

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=4,
            ensure_ascii=False
        )


async def process_review_background(
    review_id: str,
    review_text: str
):

    logger.info(
        f"Background processing started: review_id={review_id}"
    )

    try:

        response = await client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": """
You are a customer review analyzer.

Analyze the review and return ONLY valid JSON.

Required format:

{
    "sentiment": "Positive",
    "summary": "short summary"
}

Sentiment must be exactly one of:
Positive
Negative
Neutral

The summary should be short and clear.
"""
                },
                {
                    "role": "user",
                    "content": review_text
                }
            ],
            temperature=0
        )

        ai_text = response.choices[0].message.content.strip()

        result = json.loads(ai_text)

        if "sentiment" not in result:
            raise ValueError("AI response missing sentiment")

        if "summary" not in result:
            raise ValueError("AI response missing summary")

        final_result = {
            "review_id": review_id,
            "status": "completed",
            "sentiment": result["sentiment"],
            "summary": result["summary"],
            "processed_at": datetime.now().isoformat()
        }

        save_result(
            review_id,
            final_result
        )

        logger.info(
            f"Background processing completed: review_id={review_id}"
        )

    except Exception as e:

        logger.exception(
            f"Background processing failed: review_id={review_id}"
        )

        failed_result = {
            "review_id": review_id,
            "status": "failed",
            "message": str(e),
            "processed_at": datetime.now().isoformat()
        }

        save_result(
            review_id,
            failed_result
        )