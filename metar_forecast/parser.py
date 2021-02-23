import os
from datetime import datetime

from rich.progress import track

from .models.console import console
from .models.metar_model import Metar

TODAY = datetime.now()


def _handle_metar_code(code: str):
    metar_date = code[0:12]
    metar = code[13:]
    date = datetime.strptime(metar_date, "%Y%m%d%H%M")
    return date, metar


def parse_metars_from_file(station: str, start_year=2005, end_year=TODAY.year):
    main_path = os.path.dirname(__file__)

    for year in range(start_year, end_year):
        path = main_path + f"/data/{station}/{year}.txt"
        lines = open(path, "r").readlines()
        message = f"{station}: {year}..."
        for n in track(range(len(lines)), description=message):
            metar_date, metar_code = _handle_metar_code(lines[n].replace("=", ""))

            try:
                metar = Metar(metar_date, metar_code)
            except Exception as error:
                console.print(f"\n\n{lines[n]}", style="info")
                console.print("Parser error: ", end="", style="danger")
                console.print(f"{error}", style="warning")
                error = 1
                exit()
            yield metar


def write_csv(station: str, start_year=2005, end_year=TODAY.year):
    main_path = os.path.dirname(__file__)
    csv = open(main_path + f"/data/{station}/data.csv", "w")

    count = 0
    for metar in parse_metars_from_file(
        station, start_year=start_year, end_year=end_year
    ):
        d = metar.to_dict()
        if count == 0:
            csv.write(",".join(header.capitalize() for header in d.keys()))
            csv.write("\n")
        count += 1
        csv.write(",".join(str(value) for value in d.values()))
        csv.write("\n")
        yield list(metar.to_dict().keys())
