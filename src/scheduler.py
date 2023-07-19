from rocketry import Rocketry
from rocketry.conds import daily

from .forecast import make_forecast
from .tojson import to_json
from .to_txt import to_txt


# Creating the Rocketry app
app = Rocketry(config={"task_execution": "async"})


async def forecasts(stations):
    for station in stations:
        json = await make_forecast(station)
        to_json(station, json)
        to_txt(station)


from datetime import datetime, timedelta

today = datetime.now()


def dt2hmstr(dt: datetime) -> str:
    return dt.strftime("%H:%M")


# Creating some tasks
# @app.task(f"time of day between {dt2hmstr(today)} and {dt2hmstr(todayplus1min)}")
@app.task(daily.at(dt2hmstr(today)))
async def forecasts_at_XXz():
    stations = ["mroc", "mrpv", "mrlb", "mrlm"]
    await forecasts(stations)
    ...


@app.task(daily.at("06:10"))
async def forecasts_at_12z():
    stations = ["mrpv", "mrlb", "mrlm"]
    await forecasts(stations)
    ...


@app.task(daily.at("05:10"))
async def forecasts_at_11z():
    stations = ["mroc"]
    await forecasts(stations)
    ...


@app.task(daily.at("11:10"))
async def forecasts_at_17z():
    stations = ["mroc", "mrlb"]
    await forecasts(stations)
    ...


@app.task(daily.at("17:10"))
async def forecasts_at_23z():
    stations = ["mroc"]
    await forecasts(stations)
    ...


@app.task(daily.at("23:10"))
async def forecasts_at_05z():
    stations = ["mroc"]
    await forecasts(stations)
    ...


if __name__ == "__main__":
    # If this script is run, only Rocketry is run
    app.run()
