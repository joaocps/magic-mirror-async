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
    def current_temperature(self):
        return self._data['current']['temp']

    @property
    def current_description(self):
        return self._data['current']['weather'][0]['description']

    @property
    def alert(self):
        if 'alerts' in self._data:
            return self._data['alerts']['description']
        else:
            return False

    @property
    def forecast(self):
        return self._data['daily'][0]['dt']

    def __repr__(self):
        return f'{self.current_temperature}º right now'
