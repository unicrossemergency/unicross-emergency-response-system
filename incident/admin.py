from django.contrib import admin
from .models import Incident,SMSLog
from django.utils import timezone
from django.utils.html import format_html
from .services import send_status_sms
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):

    list_display = (
        "incident_type",
        "location_text",
        "status_tag",
        "incident_priority",
        "is_anonymous",
        "created_at",
    )

    list_filter = ("incident_type", "status","is_anonymous")

    search_fields = ("location_text", "description","name","phone")

    ordering = ("-created_at",)

    # 🔥 THIS IS THE MAP FUNCTION
    def location_map(self, obj):
        if obj.latitude is not None and obj.longitude is not None:
            return format_html(
                '''
                <a href="https://www.google.com/maps?q={},{}" target="_blank">
                Open Full Map
                </a>
                <br><br>
                <iframe
                    width="100%"
                    height="350"
                    style="border:0; border-radius:12px;"
                    loading="lazy"
                    src="https://maps.google.com/maps?q={},{}&z=16&output=embed">
                </iframe>
                ''',
                obj.latitude, obj.longitude, # for link
                obj.latitude, obj.longitude  # for iframe
            )
        return "No GPS location available"

    location_map.short_description = "Live Map"

    readonly_fields = ("location_map", "created_at", "updated_at")

    fieldsets = (

        ("🚨 Incident Details", {
            "fields": ("incident_type", "description", "status")
        }),

        ("👤 Reporter Info", {
            "fields": ("name", "phone", "is_anonymous")
        }),

        ("📍 Location", {
            "fields": ("location_text", "latitude", "longitude", "location_map")
        }),

        ("🚑 Response", {
            "fields": ("acknowledged_by", "scene_image")
        }),

        ("⏱️ System Info", {
            "fields": ("created_at", "updated_at")
        }),
    )


    # 🔥 ROLE FILTER (IMPORTANT SECURITY LAYER)
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        if hasattr(request.user, "role") and request.user.role:
            return qs.filter(incident_type=request.user.role).order_by("-created_at")

        return qs.none()
    
    def get_fields(self, request, obj=None):

        if request.user.is_superuser:
            return "__all__"

        # STAFF VIEW ONLY
        return (
            "incident_type",
            "description",
            "location_text",
            "latitude",
            "longitude",
            "name",
            "phone",
            "is_anonymous",
            "status",
            "scene_image",
            "acknowledged_by",
            "location_map",
            "created_at",
        )

    def get_readonly_fields(self, request, obj=None):

        if request.user.is_superuser:
            return self.readonly_fields

        return (
            "incident_type",
            "description",
            "location_text",
            "latitude",
            "longitude",
            "name",
            "phone",
            "is_anonymous",
            "created_at",
            "updated_at",
            "location_map",
            "acknowledged_by"
        )
        
  # 🔥 ACTIONS (DISPATCH ENGINE)

    def acknowledge(self, request, queryset):

        channel_layer = get_channel_layer()

        for incident in queryset:
            incident.status = "acknowledged"
            incident.acknowledged_by = request.user
            incident.save()

            # send SMS
            send_status_sms(
                incident,
                "acknowledged"
            )

            # realtime frontend update
            async_to_sync(channel_layer.group_send)(
                "incidents",
                {
                    "type": "status_update",
                    "data": {
                        "id": incident.id,
                        "status": incident.status,
                        "incident_type": incident.incident_type,
                    }
                }
            )

    def dispatch(self, request, queryset):

        channel_layer = get_channel_layer()
        print("📡 ABOUT TO SEND WS MESSAGE")

        for incident in queryset:

            print(
                "🔥 ADMIN ACTION TRIGGERED:",
                incident.id,
                incident.status
            )

            incident.status = "dispatched"
            incident.acknowledged_by = request.user
            incident.save()

            send_status_sms(
                incident,
                "dispatched"
            )

            async_to_sync(channel_layer.group_send)(
                "incidents",
                {
                    "type": "status_update",
                    "data": {
                        "id": incident.id,
                        "status": incident.status,
                        "incident_type": incident.incident_type,
                        "message_type": "status_update"
                    }
                }
            )


    def mark_on_scene(self, request, queryset):

        channel_layer = get_channel_layer()

        for incident in queryset:
            incident.status = "on_scene"
            incident.acknowledged_by = request.user
            incident.save()

            send_status_sms(
                incident,
                "on_scene"
            )

            async_to_sync(channel_layer.group_send)(
                "incidents",
                {
                    "type": "status_update",
                    "data": {
                        "id": incident.id,
                        "status": incident.status,
                        "incident_type": incident.incident_type,
                    }
                }
            )


    def resolve(self, request, queryset):

        channel_layer = get_channel_layer()

        for incident in queryset:
            incident.status = "resolved"
            incident.acknowledged_by = request.user
            incident.save()

            send_status_sms(
                incident,
                "resolved"
            )

            async_to_sync(channel_layer.group_send)(
                "incidents",
                {
                    "type": "status_update",
                    "data": {
                        "id": incident.id,
                        "status": incident.status,
                        "incident_type": incident.incident_type,
                    }
                }
            )


    actions = ["acknowledge", "dispatch", "mark_on_scene", "resolve"]

    def save_model(self, request, obj, form, change):

        if change:

            old_obj = Incident.objects.get(pk=obj.pk)

            # ✅ ONLY RUN WHEN STATUS CHANGES
            if old_obj.status != obj.status:
                super().save_model(request, obj, form, change)

                # 🔥 AUTO ASSIGN STAFF WHO MADE THE CHANGE
                #if not request.user.is_superuser:
                Incident.objects.filter(pk=obj.pk).update(
                acknowledged_by=request.user )

                obj.refresh_from_db()

                # SMS
                send_status_sms(obj, obj.status)

                channel_layer = get_channel_layer()

                # WebSocket update
                async_to_sync(channel_layer.group_send)(
                    "incidents",
                    {
                        "type": "status_update",
                        "data": {
                            "id": obj.id,
                            "status": obj.status,
                            "incident_type": obj.incident_type,
                            #"acknowledged_by": request.user.email
                            #"acknowledged_by": request.user.username if request.user else None
                        }
                    }
                )
                return

        super().save_model(request, obj, form, change)

    def status_tag(self, obj):
        colors = {
            "submitted": "orange",
            "acknowledged": "blue",
            "dispatched": "purple",
            "on_scene": "darkgreen",
            "resolved": "green",
        }

        color = colors.get(obj.status, "black")

        return format_html(
            '<span style="color:white; background:{}; padding:4px 8px; border-radius:6px;">{}</span>',
            color,
            obj.status.upper()
        )

    status_tag.short_description = "Status"

    def incident_priority(self, obj):
        if obj.incident_type == "fire":
            return "🔥 HIGH"
        elif obj.incident_type == "crime":
            return "🚨 MEDIUM"
        elif obj.incident_type == "health":
            return "HIGH"
        else:
            return "⚪ NORMAL"

    incident_priority.short_description = "Priority"
    
    class Media:
        js = ("js/admin_incident_ws.js",)


# =====================================================
# SMS LOG ADMIN
# =====================================================

@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):

    list_display = (
        "phone",
        "department",
        "sms_type",
        "status",
        "created_at",
    )

    search_fields = (
        "phone",
        "department",
        "message"
    )

    list_filter = (
        "department",
        "status",
    )

    ordering = ("-created_at",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        if hasattr(request.user, "role") and request.user.role:

            return qs.filter(
                department=request.user.role
            ).order_by("-created_at")

        return qs.none()
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or (
            request.user.is_staff and hasattr(request.user, "role")
        )

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or (
            request.user.is_staff and hasattr(request.user, "role")
        )

    def has_add_permission(self, request):
        return request.user.is_superuser or (
            request.user.is_staff and hasattr(request.user, "role")
        )

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser