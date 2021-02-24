import os
import re
from calendar import monthrange
from datetime import datetime
from time import sleep

from bs4 import BeautifulSoup
from requests import get
from rich.progress import track

from .models.console import console
from .models.metar_model import Metar

MAIN_PATH = os.path.dirname(__file__)
TODAY = datetime.now()
OGIMET_LIMIT_MESAGE = "#Sorry, Your quota limit for slow queries rate has been reached"


class OgimetLimitError(Exception):
    """
    #Sorry, Your quota limit for slow queries rate has been reached

    The anterior message is raised by Ogimet.com when you get a request
    one after another. So, you must to wait at less five minutes to ensure
    succesful request of METAR data.

    This exception is raised when that message is detected.
    """

    def __init__(self, message=OGIMET_LIMIT_MESAGE):
        super().__init__(message)


def _join_line_separated_metars(metar_list):
    """Joins the metar when it is separated in several lines

    Args:
        metar_list (list): The Metar list from file lines without fromating

    Returns:
        list: The correct Metar list, one Metar by item
    """
    metar = ""
    correct_metar_list = []
    for line in metar_list:
        metar += re.sub(r"^\s{2,}", " ", line)
        if "=" in line:
            correct_metar_list.append(metar)
            metar = ""

    return correct_metar_list


def _handle_metar(most_recent_metar):
    """Handles the most recent Metar

    Args:
        most_recent_metar (list): The request from "download_most_recent_metar" function
    """
    date = datetime.strptime(most_recent_metar[0], "%Y/%m/%d %H:%M")

    return Metar(date, most_recent_metar[1])


def download_metars_by_year(station_icao, start_year=2005, end_year=TODAY.year):
    remaining_time_to_request = 30

    for year in range(start_year, end_year):
        try:
            os.mkdir(MAIN_PATH + "/downloads")
        except Exception as error:
            pass
        f = open(MAIN_PATH + f"/downloads/{year}.txt", "w")

        for month in range(1, 13):
            date = datetime(year, month, 1, 0, 0, 0)
            month_range = monthrange(year=date.year, month=date.month)
            date_str = f'{datetime.strftime(date, "%Y-%m")}'
            url = f"http://ogimet.com/display_metars2.php?lugar={station_icao}&tipo=SA&ord=DIR&nil=SI&fmt=txt&ano={date.year}&mes={date.month}&day={date.day}&hora=00&anof={date.year}&mesf={date.month}&dayf={month_range[1]}&horaf=23&minf=59&enviar=Ver"
            # print(f'URL: {url}')
            # url = 'https://www.aviationweather.gov/metar/data?ids=MROC+MRPV+MRLM+MRLB&format=raw&date=&hours=24&taf=on'

            while True:
                console.print(f"[yellow]Request -> Year:{year} / Month: {month}")
                try:
                    res = get(url)
                    html_soup = BeautifulSoup(res.text, "html.parser")
                    metars_text = html_soup.find("pre").text
                    if OGIMET_LIMIT_MESAGE in metars_text:
                        remaining_time_to_request = 300
                        raise OgimetLimitError()
                    metars_text = _join_line_separated_metars(metars_text.split("\n"))
                    for line in metars_text:
                        if metars_text.index(line) == 0:
                            f.write(line[568:] + "\n")
                        else:
                            f.write(line + "\n")
                    console.print(f"\n[green]Request succesfully.")
                    break
                except Exception as error:
                    console.print(f"\n\n[white]{url}\n")
                    console.print(f"[bold rgb(175,0,0)]Request Error: ", end="")
                    console.print(f"[italic rgb(175,175,0)]{error}\n")
                    for sec in track(
                        range(remaining_time_to_request),
                        description="Remaining for next request...",
                    ):
                        sleep(1)

            for sec in track(
                range(remaining_time_to_request),
                description="Remaining for next request...",
            ):
                sleep(1)
            os.system("clear")
        f.close()


def download_most_recent_metar(station_icao):
    url = f"http://tgftp.nws.noaa.gov/data/observations/metar/stations/{station_icao.upper()}.TXT"
    # print(url)
    try:
        res = get(url)
        res = res.text.split("\n")
        res = res[:2]
        metar = _handle_metar(res)
        console.print("\n{}".format(metar.string()), style='success')
    except Exception as error:
        console.print(f"\n\n{url}", style="info")
        console.print(f"Request Error: ", end="", style="danger")
        console.print(f"{error}", style="warning")
        return None

    return res


if __name__ == "__main__":
    download_metars_by_year("MROC")
