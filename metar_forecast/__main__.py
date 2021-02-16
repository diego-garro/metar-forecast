import click
from click.decorators import argument

from .models.logger_model import logger
from .parser import parse_metars_from_file


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


if __name__ == "__main__":
    forecast()
