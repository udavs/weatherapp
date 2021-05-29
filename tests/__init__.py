from django.urls import reverse

from weatherapp.settings import WEATHER_API_URL, WEATHER_API_KEY

TEST_DATE = "2021-06-03"
TEST_AVG_TEMP = "10.2"
TEST_COUNTRY_CODE = "UK"
TEST_WEATHER_API_URL = f"{WEATHER_API_URL}/forecast.json?key={WEATHER_API_KEY}&q={TEST_COUNTRY_CODE}&dt={TEST_DATE}&aqi=no"
WEATHER_FORECAST_ENDPOINT = url = reverse("weather-forecast")
