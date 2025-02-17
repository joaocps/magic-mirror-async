import json
import logging
import aiohttp

from library.news import News
from library.weather import Weather

LOGGER = logging.getLogger(__name__)

API_NEWS_PORTUGAL = "https://news.google.com/rss?hl=pt-PT&gl=PT&ceid=PT:pt-150"
API_NEWS_UK = "https://news.google.com/rss?hl=en-GB&gl=GB&ceid=GB:en-150"


class NEWS_API:  # pylint: disable=invalid-name
    """Interfaces to https://news.google.com/"""

    def __init__(self, websession):
        self.websession = websession

    async def retrieve(self, url, **kwargs):
        """Issue API requests."""
        try:
            async with self.websession.request(
                    "GET", url, headers={"Referer": "https://news.google.com/"}, **kwargs
            ) as res:
                if res.status != 200:
                    raise Exception("Could not retrieve information from API")
                if res.content_type == "application/json":
                    LOGGER.info("JSON content retrieved from Google News")
                    return await res.json()
                LOGGER.info("Text content retrieved from Google News")
                return await res.text()
        except aiohttp.ClientError as err:
            LOGGER.error(err)
        except json.decoder.JSONDecodeError as err:
            LOGGER.error(err)


class WEATHER_API:  # pylint: disable=invalid-name
    """Interfaces to https://openweathermap.org/"""

    def __init__(self, websession):
        self.websession = websession

    async def retrieve(self, url, **kwargs):
        """Issue API requests."""
        try:
            async with self.websession.request(
                    "GET", url, headers={"Referer": "https://openweathermap.org/"}, **kwargs
            ) as res:
                if res.status != 200:
                    raise Exception("Could not retrieve information from API")
                if res.content_type == "application/json":
                    LOGGER.info("JSON content retrieved from Open Weather")
                    return await res.json()
                LOGGER.info("Text content retrieved from Open Weather")
                return await res.text()
        except aiohttp.ClientError as err:
            LOGGER.error(err)
        except json.decoder.JSONDecodeError as err:
            LOGGER.error(err)


class NewsLocation:
    def __init__(self, country):
        self.country = country

    async def get(self, api):
        if self.country == "pt":
            raw_news = await api.retrieve(url=API_NEWS_PORTUGAL)
            if raw_news is not None:
                news = News(raw_news)
                return news.titles
            return ['No Internet Connection']
        if self.country == "uk":
            raw_news = await api.retrieve(url=API_NEWS_UK)
            if raw_news is not None:
                news = News(raw_news)
                return news.titles
            return ['No Internet Connection']


class WeatherLocation:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
        self.url = 'https://api.openweathermap.org'
        self.key = 'f15d322fc88c404f0560bf7423da5a98'
        self.lang = 'pt'
        self.units = 'metric'

    async def get(self, api):
        formatted_url = f'{self.url}/data/2.5/onecall' \
                        f'?lat={self.latitude}' \
                        f'&lon={self.longitude}' \
                        f'&appid={self.key}' \
                        f'&lang={self.lang}' \
                        f'&units={self.units}'
        raw_weather = await api.retrieve(url=formatted_url)
        if raw_weather is not None:
            formatted_weather = Weather(raw_weather)
            return formatted_weather
        return None
