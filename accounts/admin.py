from django.contrib import admin
from .models import User, Rate


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_lector")
    list_filter = ("is_lector",)
    search_fields = ("username", "email", "first_name", "last_name",)
    fields = ("username",
              "email",
              "first_name",
              "last_name",
              "is_lector",
              "is_active",
              "location",
              "phone",
              "photo",
              "_description")


@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    list_display = ("lector", "rate", "comment")
    search_fields = ("lector__username", "comment")
