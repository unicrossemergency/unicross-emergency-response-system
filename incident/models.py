from django.db import models
from django.conf import settings


class Incident(models.Model):

    INCIDENT_TYPES = (
        ('fire', 'Fire'),
        ('crime', 'Crime'),
        ('health', 'Health'),
        ('accident', 'Accident'),
        ('other', 'Other'),
    )

    STATUS_CHOICES = (
        ('submitted', 'Submitted'),
        ('acknowledged', 'Acknowledged'),
        ('dispatched', 'Dispatched'),
        ('on_scene', 'On Scene'),
        ('resolved', 'Resolved'),
    )

    # Reporter
    name = models.CharField(max_length=150, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    is_anonymous = models.BooleanField(default=False)

    # Incident info
    incident_type = models.CharField(max_length=20, choices=INCIDENT_TYPES)
    description = models.TextField()

    # Location
    location_text = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    # Status engine
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')

     # =========================
    # STAFF ASSIGNMENT (IMPORTANT ADDITION)
    # =========================
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_incidents"
    )


    # Staff tracking
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Evidence
    scene_image = models.ImageField(upload_to="incident_images/", null=True, blank=True)

    # Timeline
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def display_name(self):
        return "Anonymous" if self.is_anonymous else self.name
    
    def has_location(self):
        return self.latitude is not None and self.longitude is not None

    def __str__(self):
        return f"{self.incident_type} - {self.status}"
    
    
    def save(self, *args, **kwargs):
        send_sms_flag = False
        old_status = None

        if self.pk:
            old = Incident.objects.get(pk=self.pk)
            old_status = old.status

            # only trigger if status actually changed
            if old.status != self.status:
                send_sms_flag = True
        else:
            send_sms_flag = True  # new incident (optional future SMS)

        super().save(*args, **kwargs)

        # ONLY SEND SMS ON REAL CHANGE
        if send_sms_flag and old_status != self.status:

            from .services import send_status_sms
            send_status_sms(self, self.status)


class SMSLog(models.Model):

    SMS_TYPES = (
        ("new_incident", "New Incident"),
        ("incident_update", "Incident Update"),
    )

    phone = models.CharField(max_length=20)

    department = models.CharField(max_length=100)

    message = models.TextField()
    sms_type = models.CharField(
        max_length=30,
        choices=SMS_TYPES,
        default="new_incident"
    )

    status = models.CharField(
        max_length=20,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.department} - {self.phone}"
    

    