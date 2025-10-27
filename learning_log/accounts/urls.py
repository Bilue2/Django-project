"""Defines URL patterns for users' accounts."""

from django.urls import path, include

from . import views

app_name = "accounts"
urlpatterns = [
    # Include default auth urls.
    path("", include("django.contrib.auth.urls")),
    # Register page.
    path("register/", views.register, name="register"),

]