import json
from typing import Dict


def read_json_file(station: str) -> Dict[str, Dict[str, str]]:
    f = open(f"data/json/{station}.json")
    json_obj = json.load(f)
    f.close()
    return json_obj


def to_txt(station: str) -> None:
    json_obj = read_json_file(station)
    txt = "Hour (UTC)".rjust(15)
    keys = list(json_obj.keys())
    for key in keys:
        txt += key.capitalize().rjust(15)

    hours = list(json_obj[keys[0]].keys())
    for hour in hours:
        txt += "\n" + hour.rjust(15)
        for key in keys:
            data = json_obj[key][hour]
            txt += data.rjust(15)

    f = open(f"data/txt/{station}.txt", "w")
    f.write(txt)
    f.close()


if __name__ == "__main__":
    stations = ["mroc", "mrpv", "mrlb", "mrlm"]
    for stn in stations:
        to_txt(stn)
