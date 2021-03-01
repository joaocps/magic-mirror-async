from datetime import datetime
import logging

LOGGER = logging.getLogger(__name__)


class WeatherForecast:
    """Represents forecast object"""

    def __init__(self, data):
        self._data = data

    @property
    def week_day(self):
        return datetime.utcfromtimestamp(self._data['dt']).strftime('%A')

    @property
    def min_temperature(self):
        return round(self._data['temp']['min'], 1)

    @property
    def max_temperature(self):
        return round(self._data['temp']['max'], 1)

    @property
    def rain_probability(self):
        return self._data['pop']

    @property
    def short_description(self):
        return self._data['weather'][0]['main']

    @property
    def full_description(self):
        return self._data['weather'][0]['description']

    def __repr__(self):
        return f"Forecast for {self.week_day}"