from django.urls import path

from . import views

urlpatterns = [path("", views.GettingWeatherAPI.as_view(), name="weather-forecast")]
