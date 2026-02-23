from flask_jwt_extended import create_access_token
from repositories.user_repo import UserRepository
from core.errors import AuthenticationError

class AuthService:
    @staticmethod
    def verify_otp_and_login(phone, otp):
        # In production, check against your SMS gateway/Redis OTP store
        if otp != "123456": # Placeholder for actual logic
            raise AuthenticationError("Invalid OTP provided")
        
        user = UserRepository.get_by_phone(phone)
        if not user:
            # Auto-register as customer if not found
            user = UserRepository.create(phone=phone, role="customer")
        
        # Create token with role claim
        access_token = create_access_token(
            identity=user.id, 
            additional_claims={"role": user.role}
        )
        
        return {"token": access_token, "user": user.to_dict()}
