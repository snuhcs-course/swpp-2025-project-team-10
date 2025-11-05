"""
URL configuration for barter app.
"""

from django.urls import path

from . import views

app_name = "barter"

urlpatterns = [
    path(
        "requests/create/",
        views.create_barter_request,
        name="create-request",
    ),
    path(
        "requests/<uuid:request_id>/accept/",
        views.accept_barter_request,
        name="accept-request",
    ),
    path(
        "requests/<uuid:request_id>/reject/",
        views.reject_barter_request,
        name="reject-request",
    ),
]
