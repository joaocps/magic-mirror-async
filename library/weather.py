import logging

LOGGER = logging.getLogger(__name__)


class Weather:
    """Represents current weather and forecast"""
    def __init__(self, data):
        self._data = data

    @property
    def timezone(self):
        return self._data["timezone"]
