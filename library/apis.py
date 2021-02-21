import ast
import json
import logging
import aiohttp

from library.news import News

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

API_NEWS_PORTUGAL = "https://news.google.com/rss?hl=pt-PT&gl=PT&ceid=PT:pt-150"
API_NEWS_UK = "https://news.google.com/rss?hl=en-GB&gl=GB&ceid=GB:en-150"


# needs &output=rss ??

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
                    return await res.json()
                return await res.text()
        except aiohttp.ClientError as err:
            LOGGER.error(err)
        except json.decoder.JSONDecodeError as err:
            LOGGER.error(err)


class NewsLocation:

    @classmethod
    async def get(cls, api, country):
        if country == "pt":
            raw_news = await api.retrieve(url=API_NEWS_PORTUGAL)
            news = News(raw_news)
            return news.titles
        if country == "uk":
            raw_news = await api.retrieve(url=API_NEWS_UK)
            news = News(raw_news)
            return news.titles

