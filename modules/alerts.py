import os
import time
from twilio.rest import Client
import streamlit as st

# Global dictionary to track last alert time for each type (Simulated persistent state)
# In production, use a database or session state
_last_alert_time = {}

def send_whatsapp_alert(message, account_sid, auth_token, from_number, to_number, cooldown=30):
    """
    Sends a WhatsApp alert using Twilio with duplicate prevention logic.
    """
    global _last_alert_time
    current_time = time.time()
    
    if "emergency" in _last_alert_time:
        elapsed = current_time - _last_alert_time["emergency"]
        if elapsed < cooldown:
            return False, f"Cooldown active ({int(cooldown - elapsed)}s remaining)"

    try:
        client = Client(account_sid, auth_token)
        
        # Twilio WhatsApp requires numbers to be prefixed with 'whatsapp:'
        wa_from = f"whatsapp:{from_number}" if not from_number.startswith("whatsapp:") else from_number
        wa_to = f"whatsapp:{to_number}" if not to_number.startswith("whatsapp:") else to_number

        msg_obj = client.messages.create(
            body=f"🆘 *VOICE HEALTH EMERGENCY*\n\n{message}",
            from_=wa_from,
            to=wa_to
        )
        
        _last_alert_time["emergency"] = current_time
        return True, msg_obj.sid
        
    except Exception as e:
        error_msg = str(e)
        if "authenticate" in error_msg.lower():
            return False, "Twilio Authentication Failed. Check SID and Token."
        if "not a valid" in error_msg.lower():
            return False, "Invalid Phone Number format."
        return False, error_msg

def trigger_logic(status, reasons, account_sid, auth_token, from_num, to_num):
    """
    Checks if a status requires an alert and triggers WhatsApp notification.
    """
    if status == "Critical":
        msg = f"Patient in CRITICAL state. Reasons: {', '.join(reasons)}"
        success, info = send_whatsapp_alert(msg, account_sid, auth_token, from_num, to_num)
        return success, info
    return False, "No critical status"
