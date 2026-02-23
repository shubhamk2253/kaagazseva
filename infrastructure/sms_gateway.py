import requests
from flask import current_app

class SMSGateway:
    @staticmethod
    def send_otp(phone, otp):
        """Standard interface for sending OTP."""
        # Example using a generic API provider
        # url = f"https://api.sms-provider.com/send?to={phone}&message=Your OTP is {otp}"
        # response = requests.get(url)
        # return response.status_code == 200
        
        # For now, we log it to console for development
        print(f"--- SMS SENT TO {phone}: Your KaagazSeva OTP is {otp} ---")
        return True

    @staticmethod
    def notify_assignment(phone, app_id):
        print(f"--- SMS SENT TO {phone}: New Application {app_id} assigned to you! ---")
        return True
