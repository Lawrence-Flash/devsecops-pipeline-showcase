"""Tickets API. Small on purpose: the pipeline is the thing being demonstrated."""

import logging
import os
import sqlite3
from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app import __version__
from app.db import connection_scope, get_ticket, init_db, insert_ticket, list_tickets
from app.models import Ticket, TicketCreate
from app.security import Settings, apply_security_headers, require_api_key

logger = logging.getLogger("tickets")


def get_db(request: Request) -> Iterator[sqlite3.Connection]:
    yield from connection_scope(request.app.state.settings.database_path)


def create_app() -> FastAPI:
    settings = Settings.from_env()
    init_db(settings.database_path)
    # headers_enabled is off: slowapi 0.1.10 tries to mutate a Response object,
    # and current FastAPI returns the endpoint value instead. The limit still applies.
    limiter = Limiter(key_func=get_remote_address, headers_enabled=False)

    app = FastAPI(
        title="Tickets API",
        version=__version__,
        # Swagger UI pulls in inline scripts that a baseline DAST scan will flag.
        # Turn docs on locally with ENABLE_OPENAPI=true when you want to explore.
        docs_url="/docs" if _docs_enabled() else None,
        redoc_url=None,
        openapi_url="/openapi.json" if _docs_enabled() else None,
    )
    app.state.limiter = limiter
    app.state.settings = settings
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        return apply_security_headers(response)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready")
    def ready(request: Request) -> dict[str, str]:
        scope = connection_scope(request.app.state.settings.database_path)
        try:
            connection = next(scope)
            connection.execute("SELECT 1")
        except sqlite3.Error as exc:
            logger.warning("readiness check failed: %s", type(exc).__name__)
            raise HTTPException(status_code=503, detail="database unavailable") from None
        finally:
            scope.close()
        return {"status": "ready"}

    @app.get("/")
    def index() -> dict[str, str]:
        return {"service": "tickets-api", "version": __version__}

    @app.post(
        "/tickets",
        status_code=201,
        response_model=Ticket,
        dependencies=[Depends(require_api_key)],
    )
    @limiter.limit(settings.rate_limit)
    def create_ticket(
        request: Request,
        payload: TicketCreate,
        connection: Annotated[sqlite3.Connection, Depends(get_db)],
    ) -> Ticket:
        del request  # slowapi needs the parameter; the handler does not.
        return insert_ticket(connection, payload.title, payload.body)

    @app.get(
        "/tickets",
        response_model=list[Ticket],
        dependencies=[Depends(require_api_key)],
    )
    @limiter.limit(settings.rate_limit)
    def read_tickets(
        request: Request,
        connection: Annotated[sqlite3.Connection, Depends(get_db)],
    ) -> list[Ticket]:
        del request
        return list_tickets(connection)

    @app.get(
        "/tickets/{ticket_id}",
        response_model=Ticket,
        dependencies=[Depends(require_api_key)],
    )
    @limiter.limit(settings.rate_limit)
    def read_ticket(
        request: Request,
        ticket_id: int,
        connection: Annotated[sqlite3.Connection, Depends(get_db)],
    ) -> Ticket:
        del request
        ticket = get_ticket(connection, ticket_id)
        if ticket is None:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return ticket

    return app


def _docs_enabled() -> bool:
    return os.environ.get("ENABLE_OPENAPI", "").strip().lower() in {"1", "true", "yes"}


app = create_app()
