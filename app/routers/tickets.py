from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.models import TicketStatus
from app.schemas import TicketCreate, TicketResponse, TicketUpdate

router = APIRouter(prefix="/tickets", tags=["tickets"])

DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "/",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new ticket",
)
def create_ticket(ticket_data: TicketCreate, db: DbSession) -> TicketResponse:
    """Create a new ticket with the provided data."""
    ticket = crud.create_ticket(db, ticket_data)
    return ticket


@router.get(
    "/",
    response_model=list[TicketResponse],
    summary="List all tickets",
)
def list_tickets(
    db: DbSession, skip: int = 0, limit: int = 100
) -> list[TicketResponse]:
    """Retrieve all tickets with optional pagination."""
    return crud.get_tickets(db, skip=skip, limit=limit)


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
    summary="Get a ticket by ID",
)
def get_ticket(ticket_id: int, db: DbSession) -> TicketResponse:
    """Retrieve a specific ticket by its ID."""
    ticket = crud.get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with id {ticket_id} not found",
        )
    return ticket


@router.put(
    "/{ticket_id}",
    response_model=TicketResponse,
    summary="Update a ticket",
)
def update_ticket(
    ticket_id: int, ticket_data: TicketUpdate, db: DbSession
) -> TicketResponse:
    """Update a ticket with the provided data.

    Note: Setting status to 'closed' via PUT is not allowed.
    Use PATCH /tickets/{ticket_id}/close instead.
    """
    ticket = crud.get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with id {ticket_id} not found",
        )

    # Business rule: Cannot set status to CLOSED via PUT
    if ticket_data.status == TicketStatus.CLOSED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot close ticket via PUT. Use PATCH /tickets/{ticket_id}/close instead",
        )

    return crud.update_ticket(db, ticket, ticket_data)


@router.patch(
    "/{ticket_id}/close",
    response_model=TicketResponse,
    summary="Close a ticket",
)
def close_ticket(ticket_id: int, db: DbSession) -> TicketResponse:
    """Close a ticket by setting its status to 'closed'."""
    ticket = crud.get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with id {ticket_id} not found",
        )

    # Business rule: Cannot close an already closed ticket
    if ticket.status == TicketStatus.CLOSED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket is already closed",
        )

    return crud.close_ticket(db, ticket)
