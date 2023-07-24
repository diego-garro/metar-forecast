import json
from typing import Dict, Any


def read_json_file(station: str) -> Dict[str, Dict[str, str]]:
    f = open(f"data/json/{station}.json")
    json_obj = json.load(f)
    f.close()
    return json_obj


def header(json_obj: Dict[str, Any]) -> None:
    dt = json_obj["datetime"]
    station = json_obj["station"]
    length = 141

    txt = f"This model ran on {dt}.".center(length)
    txt += (
        "\n"
        + f"Hourly average of variables of interest for {station['name']} ({station['icao']}).".center(
            length
        )
    )
    txt += "\n" + (
        "Model output using mean values for QNH (inHg), "
        "temperatures (°C), direction (°) and wind speed (kt)."
    ).center(length)
    # txt += "\n" + (
    #     "Instituto Meteorológico Nacional (IMN), "
    #     "Departamento de Meteorología Sinóptica y Aeronáutica (DMSA)."
    # ).center(length)
    txt += "\n" + "-" * 141
    txt += "\n" + "-" * 141
    txt += "\n"

    return txt.upper()


def to_txt(station: str) -> None:
    lenght = 20
    json_obj = read_json_file(station)
    forecasts = json_obj["forecasts"]
    txt = "Hour (UTC)".rjust(lenght)
    keys = list(forecasts.keys())
    for key in keys:
        txt += key.rjust(lenght)

    hours = list(forecasts[keys[0]].keys())
    for hour in hours:
        txt += "\n" + hour.rjust(lenght)
        for key in keys:
            data = forecasts[key][hour]
            txt += data.rjust(lenght)

    f = open(f"data/txt/{station}.txt", "w")
    f.write(header(json_obj))
    f.write(txt)
    f.close()


if __name__ == "__main__":
    stations = ["mroc", "mrpv", "mrlb", "mrlm"]
    for stn in stations:
        to_txt(stn)
