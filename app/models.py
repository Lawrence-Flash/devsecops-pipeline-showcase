"""Request and response models."""

from pydantic import BaseModel, Field, field_validator


class TicketCreate(BaseModel):
    """Payload for creating a ticket. Titles and bodies are bounded on purpose."""

    title: str = Field(min_length=1, max_length=120)
    body: str = Field(min_length=1, max_length=4000)

    @field_validator("title", "body", mode="before")
    @classmethod
    def strip_text(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value


class Ticket(BaseModel):
    id: int
    title: str
    body: str
    created_at: str
