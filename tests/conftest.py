import pytest
from backend.models import WeatherForecast
from tests import TEST_DATE, TEST_AVG_TEMP, TEST_COUNTRY_CODE


@pytest.fixture
def fill_weather_forecast_table():
    weather_forecast = WeatherForecast.objects.create(
        date=TEST_DATE, country_code=TEST_COUNTRY_CODE, avg_temp_c=TEST_AVG_TEMP
    )
    return weather_forecast
