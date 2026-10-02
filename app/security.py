"""API-key authentication and response headers for the lab API."""

import os
import secrets
from typing import Annotated

from fastapi import HTTPException, Request, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from starlette.responses import Response

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# A JSON API does not serve a document, so the browser controls are locked down.
SECURE_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": (
        "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
        "magnetometer=(), microphone=(), payment=(), usb=()"
    ),
    "Content-Security-Policy": (
        "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
    ),
    "Cross-Origin-Resource-Policy": "same-origin",
    "Cross-Origin-Opener-Policy": "same-origin",
    "X-Permitted-Cross-Domain-Policies": "none",
    "Cache-Control": "no-store",
    "Pragma": "no-cache",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "X-DNS-Prefetch-Control": "off",
}


class Settings(BaseModel):
    api_key: str
    database_path: str
    rate_limit: str

    @classmethod
    def from_env(cls) -> "Settings":
        api_key = os.environ.get("TICKETS_API_KEY", "").strip()
        # Fail closed. The lab value is injected at deploy time, never baked into the image.
        if len(api_key) < 8:
            raise RuntimeError("TICKETS_API_KEY must be set and at least 8 characters")
        database_path = os.environ.get("DATABASE_PATH", "/tmp/tickets.db").strip()
        rate_limit = os.environ.get("RATE_LIMIT", "30/minute").strip()
        return cls(
            api_key=api_key,
            database_path=database_path or "/tmp/tickets.db",
            rate_limit=rate_limit or "30/minute",
        )


def apply_security_headers(response: Response) -> Response:
    for name, value in SECURE_HEADERS.items():
        response.headers[name] = value
    if "server" in response.headers:
        del response.headers["server"]
    return response


def require_api_key(
    request: Request,
    x_api_key: Annotated[str | None, Security(api_key_header)],
) -> None:
    expected = request.app.state.settings.api_key
    if x_api_key is None or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
