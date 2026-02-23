import re
from core.errors import ValidationError

class Validator:
    @staticmethod
    def validate_phone(phone):
        """Validates Indian 10-digit phone numbers."""
        pattern = r"^[6-9]\d{9}$"
        if not re.match(pattern, phone):
            raise ValidationError("Invalid Indian phone number format")
        return True

    @staticmethod
    def validate_pincode(pincode):
        """Validates 6-digit Indian pincodes."""
        pattern = r"^\d{6}$"
        if not re.match(pattern, pincode):
            raise ValidationError("Invalid Pincode format")
        return True

    @staticmethod
    def validate_payload(data, required_fields):
        """Generic checker to ensure all required JSON keys are present."""
        missing = [field for field in required_fields if field not in data]
        if missing:
            raise ValidationError(f"Missing required fields: {', '.join(missing)}")
        return True
