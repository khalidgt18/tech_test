from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import DateTime, Integer, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TicketStatus(str, Enum):
    """Enum for ticket status values."""

    OPEN = "open"
    STALLED = "stalled"
    CLOSED = "closed"


class Ticket(Base):
    """SQLAlchemy model for tickets."""

    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[TicketStatus] = mapped_column(
        SQLEnum(TicketStatus),
        default=TicketStatus.OPEN,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
