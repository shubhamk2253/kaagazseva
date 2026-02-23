# services/ticket_service.py
from repositories.application_repo import ApplicationRepository
from models.ticket import Ticket
from extensions import db
from core.errors import ResourceNotFoundError

class TicketService:
    @staticmethod
    def raise_ticket(user_id, subject, description, app_id=None):
        """Creates a support ticket for a user."""
        ticket = Ticket(
            user_id=user_id,
            application_id=app_id,
            subject=subject,
            description=description,
            status="open"
        )
        db.session.add(ticket)
        db.session.commit()
        return ticket

    @staticmethod
    def resolve_ticket(ticket_id, admin_id, resolution_note):
        """Standardizes how admins close disputes."""
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            raise ResourceNotFoundError("Ticket not found")
        
        ticket.status = "resolved"
        ticket.resolution_note = resolution_note
        ticket.resolved_by = admin_id
        db.session.commit()
        return ticket
