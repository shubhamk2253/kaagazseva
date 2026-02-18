import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)

# ---------------- CORE SENDERS ----------------

def _log_notification(channel, mobile, message):
    log = f"[{channel}] {datetime.utcnow()} | To:{mobile} | {message}"
    print(log)
    logging.info(log)


def send_sms(mobile, message):
    """
    Replace inside with Fast2SMS / Twilio API call.
    """
    try:
        _log_notification("SMS", mobile, message)
        return True
    except Exception as e:
        logging.error(f"SMS Error: {e}")
        return False


def send_whatsapp(mobile, message):
    """
    Replace inside with WhatsApp Cloud API / Interakt call.
    """
    try:
        _log_notification("WHATSAPP", mobile, message)
        return True
    except Exception as e:
        logging.error(f"WhatsApp Error: {e}")
        return False


# ---------------- EVENT NOTIFICATIONS ----------------

def notify_application_submitted(mobile, app_id):
    msg = f"KaagazSeva: Application {app_id} received. Please complete payment to proceed."
    send_sms(mobile, msg)


def notify_payment_success(mobile, app_id, amount):
    msg = f"KaagazSeva: Payment ₹{amount} successful for {app_id}. Agent assignment in progress."
    send_whatsapp(mobile, msg)


def notify_agent_assigned(mobile, app_id, agent_name, agent_mobile):
    msg = f"KaagazSeva: Agent {agent_name} ({agent_mobile}) assigned for {app_id}."
    send_whatsapp(mobile, msg)


def notify_status_update(mobile, app_id, status):
    msg = f"KaagazSeva: Status update for {app_id}: {status}"
    send_sms(mobile, msg)
