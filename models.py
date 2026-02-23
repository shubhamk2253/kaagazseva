from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
import uuid

db = SQLAlchemy()


# =========================================================
# USERS
# =========================================================
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = db.Column(db.String(150))
    mobile = db.Column(db.String(15), unique=True, index=True)
    email = db.Column(db.String(150), unique=True)
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(50), nullable=False)  # founder | agent | customer | state_admin
    created_at = db.Column(db.DateTime, server_default=db.func.now())


# =========================================================
# AGENT REGISTRATIONS
# =========================================================
class AgentRegistration(db.Model):
    __tablename__ = "agent_registrations"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = db.Column(db.String(150))
    mobile = db.Column(db.String(15))
    email = db.Column(db.String(150))
    state_id = db.Column(db.String(50))
    district_id = db.Column(db.String(50))
    address = db.Column(db.Text)
    pincode = db.Column(db.String(10))
    status = db.Column(db.String(50), default="pending")
    created_at = db.Column(db.DateTime, server_default=db.func.now())


# =========================================================
# AGENTS
# =========================================================
class Agent(db.Model):
    __tablename__ = "agents"

    id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), primary_key=True)
    state_id = db.Column(db.String(50))
    district_id = db.Column(db.String(50))
    pincode = db.Column(db.String(10), index=True)

    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    is_verified = db.Column(db.Boolean, default=False)


# =========================================================
# PINCODES (Assignment Table)
# =========================================================
class Pincode(db.Model):
    __tablename__ = "pincodes"

    pincode = db.Column(db.String(10), primary_key=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)


# =========================================================
# APPLICATIONS
# =========================================================
class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = db.Column(db.String(20), unique=True, index=True)

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"))
    agent_id = db.Column(UUID(as_uuid=True), db.ForeignKey("agents.id"))

    name = db.Column(db.String(150))
    mobile = db.Column(db.String(15))
    service = db.Column(db.String(150))
    pincode = db.Column(db.String(10))

    status = db.Column(db.String(50))  # Pending Payment | Processing | Completed
    filename = db.Column(db.String(255))

    platform_commission = db.Column(db.Float, default=0)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime)


# =========================================================
# PAYMENTS
# =========================================================
class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = db.Column(db.String(20))
    amount = db.Column(db.Float)
    status = db.Column(db.String(50))  # Paid | refunded
    created_at = db.Column(db.DateTime, server_default=db.func.now())


# =========================================================
# AGENT WALLET
# =========================================================
class AgentWallet(db.Model):
    __tablename__ = "agent_wallets"

    agent_id = db.Column(UUID(as_uuid=True), db.ForeignKey("agents.id"), primary_key=True)
    balance = db.Column(db.Float, default=0)


# =========================================================
# WALLET TRANSACTIONS
# =========================================================
class WalletTransaction(db.Model):
    __tablename__ = "wallet_transactions"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = db.Column(UUID(as_uuid=True))
    application_id = db.Column(db.String(20))
    amount = db.Column(db.Float)
    tx_type = db.Column(db.String(20))  # credit | debit
    created_at = db.Column(db.DateTime, server_default=db.func.now())


# =========================================================
# AGENT EARNINGS
# =========================================================
class AgentEarning(db.Model):
    __tablename__ = "agent_earnings"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = db.Column(UUID(as_uuid=True))
    application_id = db.Column(db.String(20))

    service_charge = db.Column(db.Float)
    platform_commission = db.Column(db.Float)
    agent_payout = db.Column(db.Float)

    created_at = db.Column(db.DateTime, server_default=db.func.now())


# =========================================================
# TICKETS
# =========================================================
class Ticket(db.Model):
    __tablename__ = "tickets"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = db.Column(db.String(20))
    user_id = db.Column(UUID(as_uuid=True))

    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    priority = db.Column(db.String(50))

    status = db.Column(db.String(50))  # Open | Resolved
    resolution_note = db.Column(db.Text)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime)


# =========================================================
# OTP SESSIONS
# =========================================================
class OTPSession(db.Model):
    __tablename__ = "otp_sessions"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mobile = db.Column(db.String(15), index=True)
    otp_code = db.Column(db.String(6))
    expires_at = db.Column(db.DateTime)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


# =========================================================
# STATES
# =========================================================
class State(db.Model):
    __tablename__ = "states"

    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(150))


# =========================================================
# STATE SERVICES
# =========================================================
class StateService(db.Model):
    __tablename__ = "state_services"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    state_id = db.Column(db.String(50))
    service_name = db.Column(db.String(150))

    final_price = db.Column(db.Float)
    government_fee = db.Column(db.Float)
    service_fee = db.Column(db.Float)

    required_documents = db.Column(db.Text)
    processing_time = db.Column(db.String(100))

    is_active = db.Column(db.Boolean, default=True)
