import logging
import sys

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from backend.forms import COUNTRY_CODES
from backend.helpers import (
    find_existing_forecast_in_database,
    evaluate_avg_temp_into_result,
    get_weather_forecast,
    extract_date_temperature_pair,
    add_forecast_to_database,
    validate_incoming_date,
    get_location,
)
from weatherapp.settings import WEATHER_API_KEY, WEATHER_FORECAST_API

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Retrieve weather forecast for a specific date and country code."

    def add_arguments(self, parser):
        parser.add_argument("date", type=str, help="Specify a forecast date")
        parser.add_argument(
            "country_code", type=str, help="Specify a country code",
        )

    def handle(self, *args, **options):
        date = options.get("date")

        country_code = options.get("country_code")

        if country_code not in COUNTRY_CODES:
            raise CommandError("The country_code must be one of: {0}".format(COUNTRY_CODES))

        location = get_location(country_code)

        existing_forecast = find_existing_forecast_in_database(date, country_code)
        if existing_forecast:
            message = evaluate_avg_temp_into_result(existing_forecast.avg_temp_c)
            self.stdout.write(
                "The average temperature {0} for date {1} in the {2}. The result: '{3}'.".format(
                    existing_forecast.avg_temp_c, date, country_code, message
                )
            )
            sys.exit(0)

        try:
            date = validate_incoming_date(date)
            weather_forecast = get_weather_forecast(
                WEATHER_FORECAST_API, [WEATHER_API_KEY, location, date, "no"]
            )
            date_temperature_pair = extract_date_temperature_pair(weather_forecast)
            if not date_temperature_pair:
                raise CommandError("No results")

            new_forecast = add_forecast_to_database(
                date_temperature_pair[0]["date"],
                country_code,
                date_temperature_pair[0]["avgtemp_c"],
            )
            message = evaluate_avg_temp_into_result(new_forecast.avg_temp_c)

        except ValidationError as err:
            raise CommandError("Cannot retrieve weather forecast: {0}".format(err.message))

        except Exception as err:
            raise CommandError("Cannot retrieve weather forecast: {0}".format(err.args[0]))

        self.stdout.write(
            "The average temperature {0} for date {1} in the {2}. The result: '{3}'".format(
                new_forecast.avg_temp_c, date, country_code, message
            )
        )
        sys.exit(0)
