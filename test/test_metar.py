from datetime import datetime

from metar_forecast.models.metar_model import Metar

today = datetime.now()
code = "MROC 160300Z 17002KT 9999 BKN020 23/20 A3007 NOSIG"
metar = Metar(today, code)


def test_wind_dir():
    assert metar.get_wind_dir() == 170.0


def test_wind_speed():
    assert metar.get_wind_speed() == 2.0


def test_wind_gust():
    assert metar.get_wind_gust() == "null"


def test_vis():
    assert metar.get_vis() == 10000.0


def test_cavok():
    assert metar.get_cavok() == 0


def test_weather():
    assert metar.get_weather("RA") == 0
    assert metar.get_weather("FG") == 0


def test_sky():
    assert metar.get_sky_conditions() == [
        ["BKN", 2000.0, "null"],
        ["null", "null", "null"],
        ["null", "null", "null"],
        ["null", "null", "null"],
    ]


def test_temperature():
    assert metar.get_temperature() == 23.0
    assert metar.get_temperature(type="dewpoint") == 20.0


def test_pressure():
    assert metar.get_pressure() == 30.07
