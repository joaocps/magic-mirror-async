import logging
import feedparser

LOGGER = logging.getLogger(__name__)


class News:
    """Represents full news page"""

    def __init__(self, data):
        self._data = feedparser.parse(data)

    @property
    def titles(self):
        """First 3 news"""
        titles = []
        for news in self._data.entries[0:3]:
            titles.append(news.title)
        return titles

    def __repr__(self):
        return f"Top news -> {self.titles}"
