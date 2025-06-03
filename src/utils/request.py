import httpx
from typing import Dict, Union
from src.global_types import Request, Result, Credentials # Credentials might not be directly used here but good to have for context if requests get more complex

async def request_async(req: Request) -> Result[str]:
    """
    Performs an asynchronous HTTP request.
    """
    # Ensure headers is a mutable dictionary if it's None
    if req.headers is None:
        req.headers = {}

    # Set default headers
    req.headers["Origin"] = "https://labs.google"
    req.headers["Referer"] = "https://labs.google/fx/tools/whisk"

    # Commented out warning from original code:
    # if "Authorization" not in req.headers:
    #     print(f"Warning: Request is missing authorization headers: {req.url}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=req.method,
                url=req.url,
                headers=req.headers,
                content=req.body  # httpx uses 'content' for bytes/str body
            )

        response_text = response.text

        if not response.is_success: # httpx uses is_success, similar to ok
            return Result(Err=Exception(f"HTTP Error {response.status_code}: {response_text}"))

        return Result(Ok=response_text)

    except httpx.RequestError as e: # Catches connection errors, timeouts, etc.
        return Result(Err=Exception(f"Request failed: {str(e)}"))
    except Exception as e: # Catch any other unexpected errors
        return Result(Err=e if isinstance(e, Exception) else Exception("Failed to fetch."))

# For potential synchronous needs, a wrapper or a separate function would be created.
# For now, only the async version is translated as per the source.

__all__ = ["request_async"]
