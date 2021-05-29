from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save


class WeatherForecast(models.Model):
    CZ = "CZ"
    UK = "UK"
    SK = "SK"

    COUNTRY_CODES = [(UK, "United Kingdom"), (CZ, "Czech Republic"), (SK, "Slovakia")]

    country_code = models.CharField("Country Code", max_length=2, choices=COUNTRY_CODES)
    date = models.DateField("Forecast Date")
    avg_temp_c = models.FloatField("Average Temperature in Celsius")

    def __str__(self):
        return f"<{self.__class__.__name__}(county_code={self.country_code}, date={self.date}, avg_temp_c={self.avg_temp_c})>"

    @receiver(pre_save)
    def pre_save_handler(sender, instance, *args, **kwargs):
        instance.full_clean()

    class Meta:
        verbose_name = "Weather Forecast"
        verbose_name_plural = "Weather Forecasts"
