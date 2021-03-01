import asyncio
import aiohttp

from library.apis import NEWS_API, NewsLocation, WEATHER_API, WeatherLocation
from library.weather import Weather


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
        # print(weather.timezone)
        # print(weather.current_temperature)
        # print(weather.current_description)
        if weather.alert:
            print("ALERT")
        for x in weather.forecast:
            print(x.week_day)
            print(x.min_temperature)
            print(x.max_temperature)
            print(x.rain_probability)
            print(x.short_description)
            print(x.full_description)


asyncio.get_event_loop().run_until_complete(main())
