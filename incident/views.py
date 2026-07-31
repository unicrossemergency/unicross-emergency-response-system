from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import Incident
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer  # type: ignore
from .services import send_sms


# =========================================
# STAFF PHONE GROUPS
# =========================================

FIRE_STAFF = [
    "+2348011111111",
    "+2348022222222",
]

CRIME_STAFF = [
    "+2348033333333",
]

HEALTH_STAFF = [
    "+2348044444444",
]

ACCIDENT_STAFF = [
    "+2348055555555",
]


def report_incident(request):

    if request.method == "POST":

        is_anonymous = request.POST.get("anonymous") == "on"

        reporter_name = request.POST.get("reporter_name")
        phone_number = request.POST.get("phone_number")
        manual_location = request.POST.get("manual_location")

        latitude = request.POST.get("gps_latitude")
        longitude = request.POST.get("gps_longitude")

        incident_type = request.POST.get("incident_type")
        description = request.POST.get("description")

        # =========================================
        # SAFE GPS HANDLING
        # =========================================

        try:
            latitude = float(latitude) if latitude else None

        except ValueError:
            latitude = None

        try:
            longitude = float(longitude) if longitude else None

        except ValueError:
            longitude = None

        # =========================================
        # CREATE INCIDENT
        # =========================================

        incident = Incident.objects.create(
            name=None if is_anonymous else reporter_name,
            phone=None if is_anonymous else phone_number,
            location_text=manual_location,
            latitude=latitude,
            longitude=longitude,
            incident_type=incident_type,
            description=description,
            is_anonymous=is_anonymous
        )

        # =========================================
        # SIMULATED SMS ALERT SYSTEM
        # =========================================

        message = f"""
🚨 NEW EMERGENCY ALERT

TYPE: {incident_type.upper()}

LOCATION:
{manual_location}

DESCRIPTION:
{description}
"""

        # FIRE
        if incident_type == "fire":

            for phone in FIRE_STAFF:

                send_sms(
                    phone,
                    message,
                    "fire",
                    "new_incident"
                )

        # CRIME
        elif incident_type == "crime":

            for phone in CRIME_STAFF:

                send_sms(
                    phone,
                    message,
                    "crime",
                    "new_incident"
                )

        # HEALTH
        elif incident_type == "health":

            for phone in HEALTH_STAFF:

                send_sms(
                    phone,
                    message,
                    "health",
                    "new_incident"
                )

        # ACCIDENT
        elif incident_type == "accident":

            for phone in ACCIDENT_STAFF:

                send_sms(
                    phone,
                    message,
                    "accident",
                    "new_incident"
                )

        # =========================================
        # REALTIME WEBSOCKET ALERT
        # =========================================

        channel_layer = get_channel_layer()
        print("CHANNEL LAYER =", channel_layer)
        async_to_sync(channel_layer.group_send)(
            "incidents",
            {
                "type": "new_incident",
                "data": {
                    "id": incident.id,
                    "type": incident_type,
                    "description": description,
                    "location": manual_location,
                    "lat": latitude,
                    "lng": longitude,
                }
            }
        )
        print("✅ group_send finished")
        messages.success(request, "incident_success")

        return redirect("/")

    return render(request, "frontend/index.html")


# =========================================
# LIVE INCIDENT MAP API
# =========================================

def incident_data(request):

    incidents = Incident.objects.all().order_by("-created_at")

    data = []

    for i in incidents:

        if i.latitude is None or i.longitude is None:
            continue

        data.append({
            "id": i.id,
            "type": i.incident_type,
            "description": i.description,
            "location": i.location_text,
            "lat": i.latitude,
            "lng": i.longitude,
            "status": i.status,
        })

    return JsonResponse(data, safe=False)