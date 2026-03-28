from typing import Any


def success_response(data: Any = None, message: str | None = None, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "success": True,
        "message": message,
        "data": data,
        "meta": meta or {},
    }


def error_response(message: str, *, code: str, field: str | None = None) -> dict[str, Any]:
    return {
        "success": False,
        "message": message,
        "errors": [{"code": code, "field": field, "detail": message}],
    }
