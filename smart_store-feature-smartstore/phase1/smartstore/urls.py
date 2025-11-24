# smartstore/urls.py
from django.urls import path
from . import views

app_name = "smartstore"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),  # homepage
    path("api/fridges/latest/", views.api_latest_readings, name="api_latest_readings"),
    path("fridge/<int:pk>/thresholds/", views.update_thresholds, name="update_thresholds"),
    path("store/", views.store_view, name="store"),  # client form
    # path("fridge/<int:pk>/fan/", views.fan_toggle, name="fan_toggle"),
]
