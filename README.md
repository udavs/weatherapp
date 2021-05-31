# Simple weather app

This hook allows communicating with [Weather API](https://www.weatherapi.com/):
* Using the endpoint:
    - `weather-forecast` with request parameters `date` and `country_code`
* Using the django command:
    - `weather_forecast` with cli required arguments `date` and `country_code`

Please set up env vars for communication with [Weather API](https://www.weatherapi.com/):
- `WEATHER_API_URL`
- `WEATHER_API_KEY`

Please set up `SECRET_KEY` for the django app.