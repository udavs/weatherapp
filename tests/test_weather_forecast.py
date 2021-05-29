from unittest import mock

import pytest
from django.urls import reverse

from backend.models import WeatherForecast
from tests import TEST_DATE, TEST_COUNTRY_CODE, TEST_WEATHER_API_URL, WEATHER_FORECAST_ENDPOINT
from weatherapp.settings import WEATHER_API_URL, WEATHER_API_KEY


@pytest.mark.django_db
@pytest.mark.usefixtures("fill_weather_forecast_table")
@pytest.mark.parametrize(
    "date, country_code, weather_api_called, forecast_count, expected_message",
    [
        # Existing weather forecast in the database
        (TEST_DATE, TEST_COUNTRY_CODE, False, 1, "soso"),
        # New weather forecast added to the database
        ("2021-06-11", "UK", True, 2, "good"),
    ],
)
def test_get_weather_forecast_success(
    client, requests_mock, date, country_code, weather_api_called, forecast_count, expected_message
):
    mocked_weather_api = requests_mock.get(
        f"{WEATHER_API_URL}/forecast.json?key={WEATHER_API_KEY}&q={country_code}&dt={date}&aqi=no",
        json={"forecast": {"forecastday": [{"date": "2021-06-01", "day": {"avgtemp_c": 33.0}}]}},
        status_code=200,
    )

    url = reverse("weather-forecast")
    response = client.get(url, data={"date": date, "country_code": country_code})

    assert response.status_code == 200
    assert response.json()["forecast"] == expected_message
    assert mocked_weather_api.called is weather_api_called
    assert len(WeatherForecast.objects.all()) == forecast_count


@pytest.mark.django_db
def test_get_weather_forecast_failed(client, requests_mock):
    url = reverse("weather-forecast")
    requests_mock.get(
        TEST_WEATHER_API_URL, status_code=400,
    )
    response = client.get(url, data={"date": TEST_DATE, "country_code": TEST_COUNTRY_CODE})

    assert response.status_code == 400
    assert response.json()["error"] == (f"400 Client Error: None for url: {TEST_WEATHER_API_URL}")


@pytest.mark.django_db
@mock.patch("backend.views.extract_date_temperature_pair")
def test_get_weather_no_results(mocked_function, client, requests_mock):
    mocked_function.return_value = None
    requests_mock.get(
        TEST_WEATHER_API_URL, json={"forecast": {"forecastday": []}}, status_code=200,
    )
    response = client.get(
        WEATHER_FORECAST_ENDPOINT, data={"date": TEST_DATE, "country_code": TEST_COUNTRY_CODE}
    )

    assert response.status_code == 200
    assert response.json()["forecast"] == "No results"


@pytest.mark.parametrize(
    "date, country_code, err_message",
    [
        # Date in the past
        ("2020-11-12", TEST_COUNTRY_CODE, {"date": ["Obsolete date: 2020-11-12"]}),
        # Not supported country code
        (TEST_DATE, "Lisbon", {"country_code": ["Must be one of: ['CZ', 'SK', 'UK']"]}),
    ],
)
def test_get_weather_validation_failed(client, date, country_code, err_message):
    response = client.get(
        WEATHER_FORECAST_ENDPOINT, data={"date": date, "country_code": country_code}
    )

    assert response.status_code == 422
    assert response.json()["errors"] == err_message
