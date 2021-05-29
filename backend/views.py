import logging

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views import View

from backend.forms import WeatherForecastForm
from backend.helpers import (
    find_existing_forecast_in_database,
    add_forecast_to_database,
    evaluate_avg_temp_into_result,
    get_weather_forecast,
    extract_date_temperature_pair,
    get_location,
)
from weatherapp.settings import WEATHER_API_KEY, WEATHER_FORECAST_API

log = logging.getLogger(__name__)


class GettingWeatherAPI(View):
    def get(self, request):
        form = WeatherForecastForm(request.GET)
        if not form.is_valid():
            return JsonResponse({"errors": dict(form.errors.items())}, status=422)

        date = form.data.get("date")
        country_code = form.data.get("country_code")

        location = get_location(country_code)

        existing_forecast = find_existing_forecast_in_database(date, country_code)
        if existing_forecast:
            message = evaluate_avg_temp_into_result(existing_forecast.avg_temp_c)
            return JsonResponse({"forecast": message})

        try:
            weather_forecast = get_weather_forecast(
                WEATHER_FORECAST_API, [WEATHER_API_KEY, location, date, "no"]
            )
            date_temperature_pair = extract_date_temperature_pair(weather_forecast)
            if not date_temperature_pair:
                return JsonResponse({"forecast": "No results"})

            new_forecast = add_forecast_to_database(
                date_temperature_pair[0]["date"],
                country_code,
                date_temperature_pair[0]["avgtemp_c"],
            )
            message = evaluate_avg_temp_into_result(new_forecast.avg_temp_c)

        except ValidationError as err:
            log.error("Validation Error: %s", err)
            return JsonResponse({"error": err.message}, status=422)

        except Exception as err:
            log.error("ERROR: %s", err.args[0])
            return JsonResponse({"error": f"{err.args[0]}"}, status=400)

        return JsonResponse({"forecast": message})
