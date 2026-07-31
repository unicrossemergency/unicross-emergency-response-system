from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = (
        ('fire', 'Fire Staff'),
        ('crime', 'Crime Staff'),
        ('health', 'Health Staff'),
        ('accident', 'Accident Staff'),
        ('admin', 'Administrative Staff'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        null=True,
        blank=True,
        help_text="Assign emergency response role"
    )

    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def save(self, *args, **kwargs):
        # 🔥 Automatically make role users staff
        if self.role:
            self.is_staff = True
        super().save(*args, **kwargs)

    def __str__(self):
        role_display = self.get_role_display() if self.role else "No Role"
        return f"{self.email} ({role_display})"