from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"
    AGENT = "agent"
    CUSTOMER = "customer"

class ApplicationStatus(Enum):
    PENDING_PAYMENT = "pending_payment"
    PAID = "paid"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"

class PaymentStatus(Enum):
    CREATED = "created"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"
