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
from .station import Station


def get_current_metar(icao: str):
    loop = asyncio.get_event_loop()
    metar = loop.run_until_complete(fetch_metar(icao))
    return metar


def add_precipitation_column(df: pd.DataFrame) -> pd.DataFrame:
    df["precipitation"] = 0
    df.loc[
        df["weather_1"].astype(str).str.contains("RA|DZ", regex=True), "precipitation"
    ] = 1
    df.loc[
        df["weather_2"].astype(str).str.contains("RA|DZ", regex=True), "precipitation"
    ] = 1
    df.loc[
        df["weather_3"].astype(str).str.contains("RA|DZ", regex=True), "precipitation"
    ] = 1
    return df


def add_obscuration_column(df: pd.DataFrame) -> pd.DataFrame:
    df["obscuration"] = 0
    df.loc[df["weather_1"].astype(str).str.match("BR|FG|BCFG"), "obscuration"] = 1
    df.loc[df["weather_2"].astype(str).str.match("BR|FG|BCFG"), "obscuration"] = 1
    df.loc[df["weather_3"].astype(str).str.match("BR|FG|BCFG"), "obscuration"] = 1
    return df


def add_thunderstorm_column(df: pd.DataFrame) -> pd.DataFrame:
    df["thunderstorm"] = 0
    df.loc[
        df["weather_1"].astype(str).str.match(r"(\+|-)?(TS|TSRA)"), "thunderstorm"
    ] = 1
    df.loc[
        df["weather_2"].astype(str).str.match(r"(\+|-)?(TS|TSRA)"), "thunderstorm"
    ] = 1
    df.loc[
        df["weather_3"].astype(str).str.match(r"(\+|-)?(TS|TSRA)"), "thunderstorm"
    ] = 1
    return df


def add_visibility_column(df: pd.DataFrame) -> pd.DataFrame:
    df["limited_visibility"] = 0
    df.loc[df["visibility_m"].astype(float) < 5000.0, "limited_visibility"] = 1
    return df


def get_data(icao: str, metar_dt: datetime) -> pd.DataFrame:
    plus7days = metar_dt + timedelta(days=7)
    minus7days = metar_dt - timedelta(days=7)

    columns = [
        "date",
        "wind_dir_deg",
        "wind_speed_kt",
        "wind_gust_kt",
        "visibility_m",
        "weather_1",
        "weather_2",
        "weather_3",
        "temp_c",
        "dewpoint_c",
        "pressure_inhg",
    ]
    data = pd.read_csv(
        f"./data/{icao.lower()}/metars.csv", parse_dates=["date"], usecols=columns
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

    data = add_precipitation_column(data)
    data = add_obscuration_column(data)
    data = add_thunderstorm_column(data)
    data = add_visibility_column(data)

    return data


class ColumnName(SnakeCaseStrEnum):
    WindDirDeg = auto()
    WindSpeedKt = auto()
    WindGustKt = auto()
    TempC = auto()
    DewpointC = auto()
    PressureInhg = auto()
    Precipitation = auto()
    Obscuration = auto()
    Thunderstorm = auto()
    LimitedVisibility = auto()


class NumericVariable(BaseModel):
    column_name: ColumnName
    doubt: float
    value: Optional[float]


def get_days_of_interest(
    df: pd.DataFrame, vars: List[NumericVariable], metar_hour: int
) -> List[pd.Timestamp]:
    df = df.query(f"index.dt.hour == {metar_hour}")
    if len(vars) > 1:
        vars = vars[1:]
    for var in vars:
        df = df.query(
            f"{var.column_name} >= {var.value - var.doubt}"
            f" and {var.column_name} <= {var.value + var.doubt}"
        )
    return df.index.to_list()


def get_data_by_day_of_interest(
    df: pd.DataFrame, days_of_interest: List[pd.Timestamp]
) -> pd.DataFrame:
    df_of_interest = pd.DataFrame()
    for day in days_of_interest:
        df_of_interest = pd.concat(
            [
                df_of_interest,
                df.loc[str(day) : str(day + timedelta(hours=25))],
            ]
        )
    return df_of_interest


def create_dict_of_variables(metar: Metar) -> OrderedDict[str, List[NumericVariable]]:
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
                "Direction (°)",
                [
                    NumericVariable(
                        column_name=ColumnName.WindDirDeg, doubt=20.0, value=direction
                    ),
                ],
            ),
            (
                "Speed (kt)",
                [
                    NumericVariable(
                        column_name=ColumnName.WindSpeedKt, doubt=4.0, value=speed
                    ),
                ],
            ),
            (
                "Gust (kt)",
                [
                    NumericVariable(
                        column_name=ColumnName.WindGustKt, doubt=5.0, value=gust
                    ),
                ],
            ),
            (
                "Temperature (°C)",
                [
                    NumericVariable(
                        column_name=ColumnName.TempC, doubt=1.0, value=temp
                    ),
                ],
            ),
            (
                "Dewpoint (°C)",
                [
                    NumericVariable(
                        column_name=ColumnName.DewpointC, doubt=1.0, value=dewpt
                    ),
                ],
            ),
            (
                "Pressure (inHg)",
                [
                    NumericVariable(
                        column_name=ColumnName.PressureInhg, doubt=0.02, value=press
                    ),
                ],
            ),
            (
                "Precipitation Prob. (%)",
                [
                    NumericVariable(
                        column_name=ColumnName.Precipitation, doubt=0.0, value=None
                    ),
                    NumericVariable(
                        column_name=ColumnName.WindDirDeg, doubt=30.0, value=direction
                    ),
                    NumericVariable(
                        column_name=ColumnName.DewpointC, doubt=2.0, value=dewpt
                    ),
                ],
            ),
            (
                "Obscuration Prob. (%)",
                [
                    NumericVariable(
                        column_name=ColumnName.Obscuration, doubt=0.0, value=None
                    ),
                    NumericVariable(
                        column_name=ColumnName.WindDirDeg, doubt=30.0, value=direction
                    ),
                    NumericVariable(
                        column_name=ColumnName.WindSpeedKt, doubt=5.0, value=speed
                    ),
                    NumericVariable(
                        column_name=ColumnName.DewpointC, doubt=2.0, value=dewpt
                    ),
                ],
            ),
            (
                "Thunderstorm Prob. (%)",
                [
                    NumericVariable(
                        column_name=ColumnName.Thunderstorm, doubt=0.0, value=None
                    ),
                    NumericVariable(
                        column_name=ColumnName.WindDirDeg, doubt=30.0, value=direction
                    ),
                    NumericVariable(
                        column_name=ColumnName.TempC, doubt=2.0, value=temp
                    ),
                    NumericVariable(
                        column_name=ColumnName.DewpointC, doubt=2.0, value=dewpt
                    ),
                ],
            ),
            (
                "Limited Visibility Prob. (%)",
                [
                    NumericVariable(
                        column_name=ColumnName.LimitedVisibility, doubt=0.0, value=None
                    ),
                    NumericVariable(
                        column_name=ColumnName.WindDirDeg, doubt=30.0, value=direction
                    ),
                    NumericVariable(
                        column_name=ColumnName.WindSpeedKt, doubt=5.0, value=speed
                    ),
                ],
            ),
        ]
    )


def rounded(var_name: str, value: float) -> str:
    if value is np.nan:
        return "NaN"

    if var_name == ColumnName.WindDirDeg:
        value = round(value / 10) * 10
        return f"{value}"
    elif var_name in [
        ColumnName.WindSpeedKt,
        ColumnName.WindGustKt,
        ColumnName.Precipitation,
        ColumnName.Obscuration,
        ColumnName.Thunderstorm,
        ColumnName.LimitedVisibility,
    ]:
        return f"{value:.0f}"
    elif var_name in [ColumnName.TempC, ColumnName.DewpointC]:
        return f"{value:.1f}"
    else:
        return f"{value:.2f}"


def forecasting_values(
    df: pd.DataFrame, vars: List[NumericVariable], metar_date: datetime
) -> OrderedDict:
    days = get_days_of_interest(df, vars, metar_date.hour)
    df = get_data_by_day_of_interest(df, days)
    data = []
    for hours in range(1, 26):
        forecast_date = metar_date + timedelta(hours=hours)
        var = vars[0]
        try:
            forecast_df = df.query(f"index.dt.hour == {forecast_date.hour}")
            column = forecast_df[var.column_name]
            mean = column.mean(skipna=True)
            if var.column_name == ColumnName.WindGustKt:
                val_count = column.count()
                length = len(column)
                if length > 0:
                    percent = val_count / length
                else:
                    percent = np.nan
                if percent < 0.5:
                    mean = np.nan
            if len(vars) > 1 and mean != np.nan:
                mean = mean * 100
        except AttributeError:
            mean = np.nan
        data.append(
            (datetime.strftime(forecast_date, "%HZ"), rounded(var.column_name, mean))
        )
    return OrderedDict(data)


async def make_forecast(station: Station):
    metar = await fetch_metar(station.icao)
    metar_time = metar.time.time
    vars_dict = create_dict_of_variables(metar)

    data = get_data(station.icao, metar_time)
    forecasts = CllOrderedDict()
    for name, vars in vars_dict.items():
        forecasts[name] = forecasting_values(data, vars, metar_time)

    d = {
        "datetime": str(datetime.utcnow().strftime("%Y/%m/%d %H:%MZ")),
        "station": station.dict(),
        "predictor": metar.raw_code,
        "times": list(forecasts["Speed (kt)"].keys()),
        "forecasts": forecasts,
    }
    json_obj = json.dumps(d, indent=2)
    return json_obj


if __name__ == "__main__":
    asyncio.run(make_forecast("mroc"))
