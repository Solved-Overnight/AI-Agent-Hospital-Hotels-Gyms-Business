from fastapi import Request
from fastapi.responses import JSONResponse

# error handeling system for backend system


async def general_exception_handler(
    request: Request,
    exc: Exception,
):
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred.",
        },
    )