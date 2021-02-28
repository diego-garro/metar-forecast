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
    """Parse the codes of METAR reports to find coding errors.

    Args:
        station (str): ICAO station code.
        start_year (int, optional): Start year of disponible data or begin of you want to parse. Defaults to 2005.
        end_year (int, optional): End year of disponible data or until you want to parse. Defaults to TODAY.year.

    Yields:
        Metar: The METAR as a Metar object.
    """
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
    """Writes the METAR objects to a CSV file in the same folder of the data.

    Args:
        station (str): ICAO station code.
        start_year (int, optional): Start year of disponible data or begin of you want to write. Defaults to 2005.
        end_year ([type], optional): End year of disponible data or until you want to write. Defaults to TODAY.year.

    Yields:
        list: 
    """
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
        yield list(d.keys())
