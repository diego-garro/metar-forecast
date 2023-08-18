import os
from datetime import datetime

from rocketry import Rocketry
from rocketry.conds import daily, failed

from .forecast import make_forecast
from .tojson import to_json
from .to_txt import to_txt
from .station import Stations


# Creating the Rocketry app
app = Rocketry(config={"task_execution": "async"})


async def forecasts(stations: Stations):
    for station in stations:
        json = await make_forecast(station)
        to_json(station.icao, json)
        to_txt(station.icao)


today = datetime.now()


def dt2hmstr(dt: datetime) -> str:
    return dt.strftime("%H:%M")


stations = Stations()


@app.cond()
def are_there_forecasts():
    if len(os.listdir("./data/json")) < 5:
        return False
    return True


# Creating some tasks
@app.task(daily.at(dt2hmstr(today)) & ~are_there_forecasts)
async def forecasts_at_XXz():
    await forecasts(stations)
    ...


@app.task(daily.at("06:10"))
async def forecasts_at_12z():
    await forecasts(stations[1:])
    ...


@app.task(daily.at("05:10"))
async def forecasts_at_11z():
    await forecasts([stations.mroc])
    ...


@app.task(daily.at("11:10"))
async def forecasts_at_17z():
    await forecasts(stations[:])
    ...


@app.task(daily.at("17:10"))
async def forecasts_at_23z():
    await forecasts([stations.mroc, stations.mrlb])
    ...


@app.task(daily.at("23:10"))
async def forecasts_at_05z():
    await forecasts([stations.mroc])
    ...


if __name__ == "__main__":
    # If this script is run, only Rocketry is run
    app.run()
