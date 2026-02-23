# core/errors.py

class KaagazSevaException(Exception):
    """Base exception for all system errors"""
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class AuthenticationError(KaagazSevaException):
    """Raised when OTP or JWT fails"""
    def __init__(self, message="Invalid credentials"):
        super().__init__(message, status_code=401)

class PaymentError(KaagazSevaException):
    """Raised when Razorpay fails or verification fails"""
    def __init__(self, message="Payment verification failed"):
        super().__init__(message, status_code=400)

class InsufficientBalanceError(KaagazSevaException):
    """Raised when agent wallet is too low for payout"""
    def __init__(self, message="Insufficient wallet balance"):
        super().__init__(message, status_code=400)

class ResourceNotFoundError(KaagazSevaException):
    """Raised when a DB record doesn't exist"""
    def __init__(self, message="The requested resource was not found"):
        super().__init__(message, status_code=404)

class ValidationError(KaagazSevaException):
    """Raised when input data is incorrect"""
    def __init__(self, message="Input validation failed"):
        super().__init__(message, status_code=422)
