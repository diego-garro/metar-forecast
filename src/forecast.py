import asyncio

from datetime import datetime, timedelta

import pandas as pd

from aeromet_py import Metar

from download import fetch_metar


def get_current_metar(station: str):
    loop = asyncio.get_event_loop()
    metar = loop.run_until_complete(fetch_metar("skbo"))
    return metar


def get_data(station: str, metar_dt: datetime) -> pd.DataFrame:
    plus7days = metar_dt + timedelta(days=7)
    minus7days = metar_dt - timedelta(days=7)

    columns = [
        "date",
        "month",
        "day",
        "hour",
        "minute",
        "wind_direction",
        "wind_speed",
        "wind_gust",
        "temperature",
        "dewpoint",
        "pressure",
    ]
    data = pd.read_csv(
        f"../data/{station.lower()}/metars.csv", parse_dates=["date"], usecols=columns
    )
    data = data.set_index(["date"])

    if plus7days.month != minus7days.month:
        data = data.query(
            f"(index.dt.month == {minus7days.month} and index.dt.day >= {minus7days.day})"
            f"or (index.dt.month == {plus7days.month} and index.dt.day <= {plus7days.day})"
        )
    else:
        data = data.query(
            f"(index.dt.month == {minus7days.month}"
            f"and (index.dt.day >= {minus7days.day} and index.dt.day <= {plus7days.day})"
        )

    return data


def main():
    station = "mrlm"
    metar = get_current_metar(station)
    data = get_data(station, metar.time.time)
    print(data.head(100))
    print(data.count())
    print(data.tail(100))


if __name__ == "__main__":
    main()
