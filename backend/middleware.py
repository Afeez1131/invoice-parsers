from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_body_size_mb: int = 2):  # e.g. 2 MB
        super().__init__(app)
        max_size_mb = max_body_size_mb * 1024 * 1024
        self.max_body_size = max_size_mb

    async def dispatch(self, request: Request, call_next):
        if request.method in ("POST", "PUT", "PATCH"):
            content_length = request.headers.get("content-length")
            if content_length:
                try:
                    size = int(content_length)
                    print(f"Content-Length: {size} bytes")
                    if size > self.max_body_size:
                        raise HTTPException(
                            status_code=413,  # Payload Too Large
                            detail=f"Request body too large. Maximum allowed: {self.max_body_size // (1024 * 1024)} MB",
                        )
                except ValueError:
                    raise HTTPException(400, "Invalid Content-Length header")

        return await call_next(request)
