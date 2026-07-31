from django.shortcuts import render
from incident.models import Incident


def home(request):

    latest_incidents = Incident.objects.exclude(
        scene_image=""
    ).order_by("-created_at")[:3]

    return render(
        request,
        "frontend/index.html",
        {
            "latest_incidents": latest_incidents
        }
    )