import time
import logging

from fastapi import Request


logger = logging.getLogger(__name__)


async def request_logging_middleware(
    request: Request,
    call_next
):

    start_time = time.perf_counter()

    response = await call_next(request)

    process_time = time.perf_counter() - start_time

    logger.info(
        f"{request.method} {request.url.path} "
        f"status={response.status_code} "
        f"time={process_time:.2f}s"
    )

    return response