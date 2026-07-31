from .models import SMSLog


def send_sms(phone, message, department, sms_type="new_incident"):

    # SAVE SMS LOG
    SMSLog.objects.create(
        phone=phone,
        message=message,
        department=department,
        sms_type=sms_type,
        status="sent"
    )

    # PRINT TO TERMINAL
    print(f"""
    ===================================
               SMS SENT
    ===================================

    TO: {phone}

    DEPARTMENT: {department}

    MESSAGE:
    {message}

    ===================================
    """)

def send_status_sms(incident, new_status):
    valid_statuses = [
        "acknowledged",
        "dispatched",
        "on_scene",
        "resolved"
    ]

    phone = incident.phone

    # ignore anonymous users (no phone)
    if not phone:
        return

    messages = {
        "acknowledged": "Your emergency has been acknowledged. Help is being prepared.",
        "dispatched": "Emergency responders have been dispatched to your location.",
        "on_scene": "Responders have arrived at your location.",
        "resolved": "Your emergency has been resolved. Stay safe.",
    }
    
    if new_status not in valid_statuses:
        return
    if new_status not in messages:
        return

    message = f"""
🚨 INCIDENT UPDATE

Type: {incident.incident_type.upper()}
Status: {new_status.upper()}

{messages[new_status]}
"""

    send_sms(
        phone=phone,
        message=message,
        department=incident.incident_type,
        sms_type="incident_update"
    )