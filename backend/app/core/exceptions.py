from fastapi import Request, status
from fastapi.responses import JSONResponse


class AppException(Exception):
    def __init__(self, detail: str, error_code: str = "BAD_REQUEST", status_code: int = status.HTTP_400_BAD_REQUEST):
        self.detail = detail
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(detail)


class ResourceNotFoundException(AppException):
    def __init__(self, detail: str = "Resource not found", error_code: str = "NOT_FOUND"):
        super().__init__(detail=detail, error_code=error_code, status_code=status.HTTP_404_NOT_FOUND)


class BadRequestException(AppException):
    def __init__(self, detail: str = "Bad request", error_code: str = "BAD_REQUEST"):
        super().__init__(detail=detail, error_code=error_code, status_code=status.HTTP_400_BAD_REQUEST)


class UnauthorizedException(AppException):
    def __init__(self, detail: str = "Unauthorized", error_code: str = "UNAUTHORIZED"):
        super().__init__(detail=detail, error_code=error_code, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(AppException):
    def __init__(self, detail: str = "Forbidden", error_code: str = "FORBIDDEN"):
        super().__init__(detail=detail, error_code=error_code, status_code=status.HTTP_403_FORBIDDEN)


class RateLimitException(AppException):
    def __init__(self, detail: str = "Too many requests. Please try again later.", error_code: str = "RATE_LIMIT_EXCEEDED"):
        super().__init__(detail=detail, error_code=error_code, status_code=status.HTTP_429_TOO_MANY_REQUESTS)



async def app_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "error_code": exc.error_code,
                "status_code": exc.status_code,
            },
        )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_SERVER_ERROR",
            "status_code": 500,
        },
    )
