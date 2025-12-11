from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import TicketStatus


class TicketCreate(BaseModel):
    """Schema for creating a new ticket."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    status: TicketStatus = TicketStatus.OPEN


class TicketUpdate(BaseModel):
    """Schema for updating a ticket (all fields optional)."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1)
    status: TicketStatus | None = None


class TicketResponse(BaseModel):
    """Schema for ticket responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    status: TicketStatus
    created_at: datetime
