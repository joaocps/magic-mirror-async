import logging

LOGGER = logging.getLogger(__name__)


class WeatherForecast:
    """Represents forecast object"""

    def __init__(self, data):
        self._data = data

    @property
    def week_day(self):
        pass

    @property
    def min_temperature(self):
        pass

    @property
    def max_temperature(self):
        pass

    @property
    def short_description(self):
        pass

    @property
    def full_description(self):
        pass

    def __repr__(self):
        return f"Forecast for {self.week_day}"