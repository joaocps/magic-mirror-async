import asyncio
import aiohttp

from library.apis import NEWS_API, NewsLocation


async def main():
    async with aiohttp.ClientSession() as session:
        api = NEWS_API(session)

        news_pt = await NewsLocation.get(api, "pt")
        news_uk = await NewsLocation.get(api, "uk")

        print(news_pt)
        print(news_uk)

asyncio.get_event_loop().run_until_complete(main())
