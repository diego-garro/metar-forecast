import os
from datetime import datetime

from rich.progress import track

from .models.console import console
from .models.metar_model import Metar

today = datetime.now()


def _handle_metar_code(code: str):
    metar_date = code[0:12]
    metar = code[13:]
    date = datetime.strptime(metar_date, "%Y%m%d%H%M")
    return date, metar


def parse_metars_from_file(station: str, start_year=2005, end_year=today.year):
    main_path = os.getcwd()

    for year in range(start_year, end_year):
        path = main_path + f"/metar_forecast/data/{station}/{year}.txt"
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
