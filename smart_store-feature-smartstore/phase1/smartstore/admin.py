from django.contrib import admin
from .models import Client, Fridge

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "phone")
    search_fields = ("first_name", "last_name", "email")

@admin.register(Fridge)
class FridgeAdmin(admin.ModelAdmin):
    list_display = ("name", "topic", "temperature", "humidity",
                    "temp_threshold", "humidity_threshold", "updated_at")
    list_editable = ("temp_threshold", "humidity_threshold")
    search_fields = ("name", "topic")
