import logging

LOGGER = logging.getLogger(__name__)


class Weather:
    """Represents current weather and forecast"""

    def __init__(self, data):
        self._data = data

    @property
    def timezone(self):
        return self._data['timezone']

    @property
    def temperature(self):
        return self._data['current']

    @property
    def description(self):
        return self._data['current']['temp']['weather']

    def __repr__(self):
        return f'{self.temperature}º right now'
