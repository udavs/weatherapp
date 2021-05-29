import datetime

from django import forms
from backend.models import WeatherForecast

COUNTRY_CODES = ["CZ", "SK", "UK"]


def validate_date(date):
    if date < datetime.date.today():
        raise forms.ValidationError(f"Obsolete date: {date}")
    return date


def validate_country_code(country_code):
    if country_code.upper() not in COUNTRY_CODES:
        raise forms.ValidationError(f"Must be one of: {COUNTRY_CODES}")
    return country_code


class WeatherForecastForm(forms.ModelForm):
    country_code = forms.CharField(validators=[validate_country_code])
    date = forms.DateField(validators=[validate_date])

    class Meta:
        model = WeatherForecast
        fields = ("country_code", "date")
