import click
from click.decorators import argument

from .downloader import download_metars_by_year, download_most_recent_metar
from .models.logger_model import logger
from .parser import parse_metars_from_file, write_csv


@click.group()
def forecast():
    pass


@forecast.command()
@click.option("-s", "--start-year", type=click.INT, help="Start year to process")
@click.option("-e", "--end-year", type=click.INT, help="End year to process")
@click.argument("station", type=click.STRING)
def parse_metars(station: str, start_year: int, end_year: int):
    if start_year is not None and end_year is not None:
        for metar in parse_metars_from_file(
            station.upper(), start_year=start_year, end_year=end_year
        ):
            pass
    elif start_year is not None:
        for metar in parse_metars_from_file(station.upper(), start_year=start_year):
            pass
    elif end_year is not None:
        for metar in parse_metars_from_file(station.upper(), end_year=end_year):
            pass
    else:
        for metar in parse_metars_from_file(station.upper()):
            pass


@forecast.command()
@click.option("-s", "--start-year", type=click.INT, help="The start year to process")
@click.option("-e", "--end-year", type=click.INT, help="The end year to process")
@click.argument("station", type=click.STRING)
def export(station: str, start_year: int, end_year: int):
    if start_year is not None and end_year is not None:
        for dic in write_csv(station.upper(), start_year=start_year, end_year=end_year):
            pass
    elif start_year is not None:
        for dic in write_csv(station.upper(), start_year=start_year):
            pass
    elif end_year is not None:
        for dic in write_csv(station.upper(), end_year=end_year):
            pass
    else:
        for dic in write_csv(station.upper()):
            pass


@forecast.command()
@click.option("-m", "--most-recent", is_flag=True)
@click.option("-s", "--start-year", type=click.INT, help="The start year to process")
@click.option("-e", "--end-year", type=click.INT, help="The end year to process")
@click.argument("station", type=click.STRING, required=True)
def download(most_recent: bool, station: str, start_year: int, end_year: int):
    if most_recent:
        download_most_recent_metar(station)
    else:
        if start_year is not None and end_year is not None:
            download_metars_by_year(station, start_year=start_year, end_year=end_year)
        elif start_year is not None:
            download_metars_by_year(station, start_year=start_year)
        elif end_year is not None:
            download_metars_by_year(station, end_year=end_year)
        else:
            download_metars_by_year(station)


if __name__ == "__main__":
    forecast()
