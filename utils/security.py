import secrets
import string
from werkzeug.security import generate_password_hash, check_password_hash

class SecurityUtils:
    @staticmethod
    def generate_otp(length=6):
        """Generates a secure numeric OTP."""
        return "".join(secrets.choice(string.digits) for _ in range(length))

    @staticmethod
    def hash_data(data):
        return generate_password_hash(data)

    @staticmethod
    def verify_hash(hashed_data, plain_data):
        return check_password_hash(hashed_data, plain_data)

    @staticmethod
    def generate_transaction_ref():
        """Creates a unique reference for internal logs."""
        return f"TXN-{secrets.token_hex(4).upper()}"
