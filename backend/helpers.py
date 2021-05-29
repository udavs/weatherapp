import logging
from typing import Dict, List

import jmespath
import requests
from django.core.exceptions import ValidationError
from django.db.models import Q
import datetime

from backend.models import WeatherForecast

log = logging.getLogger(__name__)


def evaluate_avg_temp_into_result(average_temp: float) -> str:
    if average_temp > 20:
        return "good"
    elif 10 < average_temp < 20:
        return "soso"
    else:
        return "bad"


def get_location(country_code: str) -> str:
    if country_code == "CZ":
        return "Prague"
    elif country_code == "SK":
        return "Bratislava"
    elif country_code == "UK":
        return country_code


def find_existing_forecast_in_database(date: str, country_code: str) -> WeatherForecast:
    existing_forecast = WeatherForecast.objects.filter(
        Q(date=date) & Q(country_code=country_code)
    ).first()
    if existing_forecast:
        log.debug(
            "The existing weather forecast for the date %s and country code %s already exist in database.",
            date,
            country_code,
        )
    return existing_forecast


def add_forecast_to_database(date: str, country_code: str, avg_temp: float) -> WeatherForecast:
    new_forecast = WeatherForecast.objects.create(
        date=date, country_code=country_code, avg_temp_c=avg_temp
    )
    return new_forecast


def generate_payload(key: str, country_code: str, date: str, aqi: str) -> Dict:
    return {"key": key, "q": country_code, "dt": date, "aqi": aqi}


def get_weather_forecast(weather_api_url: str, payload_data: List) -> Dict:
    response = requests.get(weather_api_url, params=generate_payload(*payload_data))
    response.raise_for_status()
    return response.json()


def extract_date_temperature_pair(forecast: Dict) -> List[Dict]:
    date_temperature_pair = jmespath.search(
        "forecast.forecastday[].{date:date, avgtemp_c:day.avgtemp_c}", forecast
    )
    return date_temperature_pair


def validate_incoming_date(date: str) -> str:
    incoming_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    if incoming_date < datetime.date.today():
        raise ValidationError(f"The obsolete date: {date}.")
    return date
