import asyncio
import aiohttp

from library.apis import NEWS_API, NewsLocation, WEATHER_API, WeatherLocation


async def main():
    async with aiohttp.ClientSession() as session:
        # api = NEWS_API(session)
        #
        # news_pt = await NewsLocation.get(api, "pt")
        # news_uk = await NewsLocation.get(api, "uk")
        #
        # print(news_pt)
        # print(news_uk)

        api2 = WEATHER_API(session)
        location = WeatherLocation(latitude=40.440811, longitude=-8.435070)
        weather = await location.get(api2)
asyncio.get_event_loop().run_until_complete(main())
