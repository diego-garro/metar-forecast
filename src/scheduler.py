from rocketry import Rocketry
from rocketry.conds import daily

from .forecast import make_forecast
from .tojson import to_json
from .to_txt import to_txt
from .station import Stations, Station


# Creating the Rocketry app
app = Rocketry(config={"task_execution": "async"})


async def forecasts(stations: Stations):
    for station in stations:
        json = await make_forecast(station)
        to_json(station.icao, json)
        to_txt(station.icao)


from datetime import datetime

today = datetime.now()


def dt2hmstr(dt: datetime) -> str:
    return dt.strftime("%H:%M")


# Creating some tasks
# @app.task(f"time of day between {dt2hmstr(today)} and {dt2hmstr(todayplus1min)}")
@app.task(daily.at(dt2hmstr(today)))
async def forecasts_at_XXz():
    await forecasts(Stations())
    ...


@app.task(daily.at("06:10"))
async def forecasts_at_12z():
    await forecasts(Stations()[1:])
    ...


@app.task(daily.at("05:10"))
async def forecasts_at_11z():
    await forecasts(Stations()[0])
    ...


@app.task(daily.at("11:10"))
async def forecasts_at_17z():
    await forecasts(Stations()[0:2])
    ...


@app.task(daily.at("17:10"))
async def forecasts_at_23z():
    await forecasts(Stations()[0])
    ...


@app.task(daily.at("23:10"))
async def forecasts_at_05z():
    await forecasts(Stations()[0])
    ...


if __name__ == "__main__":
    # If this script is run, only Rocketry is run
    app.run()
