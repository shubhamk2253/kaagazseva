from models.application import Application
from models.payment import Payment
from sqlalchemy import func

class AnalyticsService:
    @staticmethod
    def get_founder_stats():
        total_revenue = db.session.query(func.sum(Payment.amount)).filter_by(status='captured').scalar() or 0
        active_jobs = Application.query.filter(Application.status != 'completed').count()
        
        return {
            "total_revenue": total_revenue,
            "platform_profit": total_revenue * 0.20,
            "active_jobs": active_jobs
        }
