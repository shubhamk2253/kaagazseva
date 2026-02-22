from app import app
from utils.payout_scheduler import run_daily_payout

def start_payout():
    with app.app_context():
        print(f"Starting scheduled payout at 02:00 AM...")
        run_daily_payout()

if __name__ == "__main__":
    start_payout()
