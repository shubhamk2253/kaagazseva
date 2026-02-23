from datetime import datetime

class Helpers:
    @staticmethod
    def format_currency(amount):
        """Formats amount to Indian Rupee style (₹)."""
        return f"₹{amount:,.2f}"

    @staticmethod
    def get_ist_time():
        """Returns current time, can be adjusted for IST offset if needed."""
        # Render servers usually run on UTC
        return datetime.utcnow()

    @staticmethod
    def calculate_percentage(amount, percentage):
        return (amount * percentage) / 100

    @staticmethod
    def slugify(text):
        """Converts 'Service Name' to 'service-name' for URLs."""
        return text.lower().replace(" ", "-")
