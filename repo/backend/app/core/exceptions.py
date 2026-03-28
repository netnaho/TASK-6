from fastapi import HTTPException, status


class AppException(Exception):
    def __init__(self, message: str, *, code: str = "application_error", status_code: int = 400, field: str | None = None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.field = field
        super().__init__(message)


class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, code="not_found", status_code=status.HTTP_404_NOT_FOUND)


class ValidationError(AppException):
    def __init__(self, message: str, field: str | None = None):
        super().__init__(message, code="validation_error", status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, field=field)


class AuthenticationError(AppException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, code="authentication_error", status_code=status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(AppException):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, code="authorization_error", status_code=status.HTTP_403_FORBIDDEN)


class ConflictError(AppException):
    def __init__(self, message: str):
        super().__init__(message, code="conflict", status_code=status.HTTP_409_CONFLICT)


def http_401(detail: str = "Could not validate credentials") -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
