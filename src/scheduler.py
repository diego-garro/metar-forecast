from rocketry import Rocketry
from rocketry.conds import after_success

from .forecast import make_forecast
from .tojson import to_json


# Creating the Rocketry app
app = Rocketry(config={"task_execution": "async"})


async def forecasts(stations):
    for station in stations:
        json = await make_forecast(station)
        to_json(station, json)


# Creating some tasks
@app.task("time of day between 06:1 and 06:11")
async def forecasts_at_12z():
    stations = ["mrpv", "mrlb", "mrlm"]
    await forecasts(stations)
    ...


@app.task("time of day between 05:10 and 05:11")
async def forecasts_at_11z():
    stations = ["mroc"]
    await forecasts(stations)
    ...


@app.task("time of day between 11:10 and 11:11")
async def forecasts_at_17z():
    stations = ["mroc", "mrlb"]
    await forecasts(stations)
    ...


@app.task("time of day between 17:10 and 17:11")
async def forecasts_at_23z():
    stations = ["mroc"]
    await forecasts(stations)
    ...


@app.task("time of day between 23:10 and 23:11")
async def forecasts_at_05z():
    stations = ["mroc"]
    await forecasts(stations)
    ...


if __name__ == "__main__":
    # If this script is run, only Rocketry is run
    app.run()
