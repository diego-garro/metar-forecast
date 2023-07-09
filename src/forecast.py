import asyncio
import json

from collections import OrderedDict as CllOrderedDict
from datetime import datetime, timedelta
from enum import auto
from functools import wraps
from typing import List, Optional, OrderedDict

import numpy as np
import pandas as pd

from aeromet_py import Metar
from pydantic import BaseModel
from strenum import SnakeCaseStrEnum

from .download import fetch_metar


def get_current_metar(station: str):
    loop = asyncio.get_event_loop()
    metar = loop.run_until_complete(fetch_metar(station))
    return metar


def get_data(station: str, metar_dt: datetime) -> pd.DataFrame:
    plus7days = metar_dt + timedelta(days=7)
    minus7days = metar_dt - timedelta(days=7)

    columns = [
        "date",
        "year",
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
        f"./data/{station.lower()}/metars.csv", parse_dates=["date"], usecols=columns
    )
    data = data.set_index(["date"])

    if plus7days.month != minus7days.month:
        data = data.query(
            f"(index.dt.month == {minus7days.month} and index.dt.day >= {minus7days.day}) "
            f"or (index.dt.month == {plus7days.month} and index.dt.day <= {plus7days.day})"
        )
    else:
        data = data.query(
            f"index.dt.month == {minus7days.month} "
            f"and (index.dt.day >= {minus7days.day} and index.dt.day <= {plus7days.day})"
        )

    return data


class ColumnName(SnakeCaseStrEnum):
    WindDirection = auto()
    WindSpeed = auto()
    WindGust = auto()
    Temperature = auto()
    Dewpoint = auto()
    Pressure = auto()


class NumericVariable(BaseModel):
    column_name: ColumnName
    doubt: float
    value: Optional[float]


def get_days_of_interest(
    df: pd.DataFrame, var: NumericVariable, metar_hour: int
) -> List[pd.Timestamp]:
    df = df.query(f"index.dt.hour == {metar_hour}")
    df = df.query(
        f"{var.column_name} >= {var.value - var.doubt}"
        f" and {var.column_name} <= {var.value + var.doubt}"
    )
    # print(df.index.to_list())
    # print([date + timedelta(hours=12) for date in df.index.to_list()])
    return df.index.to_list()


def get_data_by_day_of_interest(
    df: pd.DataFrame, days_of_interest: List[pd.Timestamp]
) -> pd.DataFrame:
    df_of_interest = pd.DataFrame()
    for day in days_of_interest:
        df_of_interest = pd.concat(
            [
                df_of_interest,
                df.loc[str(day) : str(day + timedelta(hours=13))],
            ]
        )
    return df_of_interest


def create_dict_of_variables(metar: Metar) -> OrderedDict[str, NumericVariable]:
    direction = (
        metar.wind.direction_in_degrees
        if metar.wind.direction_in_degrees is not None
        else 180.0
    )
    speed = metar.wind.speed_in_knot if metar.wind.speed_in_knot is not None else 0.0
    gust = (
        metar.wind.gust_in_knot if metar.wind.gust_in_knot is not None else speed + 10.0
    )
    temp = (
        metar.temperatures.temperature_in_celsius
        if metar.temperatures.temperature_in_celsius is not None
        else 20.0
    )
    dewpt = (
        metar.temperatures.dewpoint_in_celsius
        if metar.temperatures.dewpoint_in_celsius is not None
        else 20.0
    )
    press = metar.pressure.in_inHg if metar.pressure.in_inHg is not None else 30.00
    return CllOrderedDict(
        [
            (
                "direction",
                NumericVariable(
                    column_name=ColumnName.WindDirection, doubt=20.0, value=direction
                ),
            ),
            (
                "speed",
                NumericVariable(
                    column_name=ColumnName.WindSpeed, doubt=4.0, value=speed
                ),
            ),
            (
                "gust",
                NumericVariable(column_name=ColumnName.WindGust, doubt=5.0, value=gust),
            ),
            (
                "temperature",
                NumericVariable(
                    column_name=ColumnName.Temperature, doubt=1.0, value=temp
                ),
            ),
            (
                "dewpoint",
                NumericVariable(
                    column_name=ColumnName.Dewpoint, doubt=1.0, value=dewpt
                ),
            ),
            (
                "pressure",
                NumericVariable(
                    column_name=ColumnName.Pressure, doubt=0.02, value=press
                ),
            ),
        ]
    )


def rounded(var_name: str, value: float) -> str:
    if value is np.nan:
        return "NaN"

    if var_name == ColumnName.WindDirection:
        value = round(value / 10) * 10
        return f"{value}"
    elif var_name in [ColumnName.WindSpeed, ColumnName.WindGust]:
        return f"{value:.0f}"
    elif var_name in [ColumnName.Temperature, ColumnName.Dewpoint]:
        return f"{value:.1f}"
    else:
        return f"{value:.2f}"


def forecasting_values(
    df: pd.DataFrame, var: NumericVariable, metar_date: datetime
) -> OrderedDict:
    days = get_days_of_interest(df, var, metar_date.hour)
    data = get_data_by_day_of_interest(df, days)
    data = []
    for hours in range(1, 14):
        forecast_date = metar_date + timedelta(hours=hours)
        forecast_df = df.query(f"index.dt.hour == {forecast_date.hour}")
        # print(forecast_df.head(10))
        mean = forecast_df[var.column_name].mean(skipna=True)
        data.append(
            (datetime.strftime(forecast_date, "%HZ"), rounded(var.column_name, mean))
        )
    return OrderedDict(data)


async def make_forecast(station: str):
    metar = await fetch_metar(station)
    metar_time = metar.time.time
    vars_dict = create_dict_of_variables(metar)

    data = get_data(station, metar_time)
    forecasts = CllOrderedDict()
    for name, var in vars_dict.items():
        forecasts[name] = forecasting_values(data, var, metar_time)

    json_obj = json.dumps(forecasts, indent=2)
    return json_obj


if __name__ == "__main__":
    asyncio.run(make_forecast("mroc"))
