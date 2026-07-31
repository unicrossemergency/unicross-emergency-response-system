from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    # 🔥 LIST VIEW (VERY IMPORTANT)
    list_display = ("email", "username", "role", "is_staff", "is_superuser")

    # 🔥 FILTER SIDEBAR
    list_filter = ("role", "is_staff", "is_superuser")

    # 🔥 SEARCH FUNCTION
    search_fields = ("email", "username")

    # 🔥 FORM STRUCTURE
    fieldsets = UserAdmin.fieldsets + (
        ("Emergency Role", {"fields": ("role",)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Emergency Role", {"fields": ("role",)}),
    )

    ordering = ("email",)