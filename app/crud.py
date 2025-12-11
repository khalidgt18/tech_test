from sqlalchemy.orm import Session

from app.models import Ticket, TicketStatus
from app.schemas import TicketCreate, TicketUpdate


def create_ticket(db: Session, ticket_data: TicketCreate) -> Ticket:
    """Create a new ticket in the database."""
    ticket = Ticket(
        title=ticket_data.title,
        description=ticket_data.description,
        status=ticket_data.status,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def get_ticket(db: Session, ticket_id: int) -> Ticket | None:
    """Get a ticket by ID."""
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()


def get_tickets(db: Session, skip: int = 0, limit: int = 100) -> list[Ticket]:
    """Get all tickets with optional pagination."""
    return db.query(Ticket).offset(skip).limit(limit).all()


def update_ticket(db: Session, ticket: Ticket, ticket_data: TicketUpdate) -> Ticket:
    """Update a ticket with the provided data."""
    update_data = ticket_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ticket, field, value)
    db.commit()
    db.refresh(ticket)
    return ticket


def close_ticket(db: Session, ticket: Ticket) -> Ticket:
    """Close a ticket by setting its status to CLOSED."""
    ticket.status = TicketStatus.CLOSED
    db.commit()
    db.refresh(ticket)
    return ticket
