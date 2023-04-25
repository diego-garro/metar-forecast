import asyncio

from datetime import datetime

import aiohttp

from aeromet_py import Metar


async def fetch_metar(station: str):
    url = f"http://tgftp.nws.noaa.gov/data/observations/metar/stations/{station.upper()}.TXT"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                text = await response.text()
                data = text.strip().split("\n")
                dt = datetime.strptime(data[0], "%Y/%m/%d %H:%M")
                return Metar(data[1], year=dt.year, month=dt.month)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    metar = loop.run_until_complete(fetch_metar("skbo"))
    print(metar)
    print(metar.raw_code)
