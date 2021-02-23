from datetime import datetime

from metar import Metar as METAR


class Metar(METAR.Metar):

    null: str = "null"

    def __init__(self, date: datetime, code: str) -> None:
        super().__init__(code, month=date.month, year=date.year)
        self.cavok = 1
        self._verify_cavok()
        if code.count("NIL") > 0:
            self.time = date
            self.cavok = Metar.null

    def _verify_cavok(self):
        if self.vis is not None and self.vis.value() < 10000.0:
            self.cavok = 0

        if len(self.weather) > 0:
            self.cavok = 0

        if len(self.sky) > 0:
            height = self.sky[0][1]
            cover = self.sky[0][0]
            if cover == "VV" or (height != None and height.value() < 6000.0):
                self.cavok = 0

    def get_wind_dir(self):
        if self.wind_dir is None:
            return Metar.null
        return self.wind_dir.value()

    def get_wind_speed(self):
        if self.wind_speed is None:
            return Metar.null
        return self.wind_speed.value()

    def get_wind_gust(self):
        if self.wind_gust is None:
            return Metar.null
        return self.wind_gust.value()

    def get_vis(self):
        if self.vis is None:
            return Metar.null
        return self.vis.value()

    def get_weather(self, weather_code: str) -> int:
        for weather in self.weather:
            if weather_code in weather:
                return 1
        return 0

    def get_cavok(self) -> int:
        return self.cavok

    def get_sky_conditions(self) -> list:
        sky_conditions = [
            [Metar.null, Metar.null, Metar.null],
            [Metar.null, Metar.null, Metar.null],
            [Metar.null, Metar.null, Metar.null],
            [Metar.null, Metar.null, Metar.null],
        ]

        for layer in self.sky:
            if "CLR" in layer:
                break
            if "NSC" in layer:
                sky_conditions[0][0] = "NSC"
                continue
            if "VV" in layer:
                sky_conditions[0][0] = "VV"
                if layer[1] is not None:
                    sky_conditions[0][1] = layer[1].value()
                continue
            index = self.sky.index(layer)
            sky_conditions[index][0] = layer[0]
            sky_conditions[index][1] = layer[1].value()
            sky_conditions[index][2] = Metar.null if layer[2] is None else layer[2]

        return sky_conditions

    def _return_value_else_null(self, var):
        return str(var.value()) if var is not None else Metar.null

    def _return_weather_else_null(self, *args):
        for arg in args:
            for tup in self.weather:
                if arg in tup:
                    return arg
        return Metar.null

    def _return_sky_layer_else_null(self, index: int, parameter="cover"):
        """Returns the value of interest in the sky variable of METAR.

        Args:
            index (int): Index of the layer to search
            parameter (str, optional): Parameter of the layer to extract. Defaults to 'cover'.
                options: 'height', 'cloud'.
        """

        if len(self.sky) > index:
            if parameter == "cover":
                return self.sky[index][0]
            elif parameter == "height":
                height = self.sky[index][1]
                return height.value() if height is not None else Metar.null
            elif parameter == "cloud":
                cloud = self.sky[index][2]
                return cloud if cloud is not None else Metar.null
        else:
            return Metar.null

    def get_temperature(self, type="absolute"):
        """Returns the absolute or dewpoint temperature or null.

        Args:
            type (str, optional): Temperature type. Defaults to 'absolute'.
                options: 'dewpoint'
        """

        if type == "absolute":
            return self.temp.value() if self.temp is not None else Metar.null
        elif type == "dewpoint":
            return self.dewpt.value() if self.dewpt is not None else Metar.null
        else:
            return Metar.null

    def get_pressure(self):
        return self.press.value() if self.press is not None else Metar.null

    def to_dict(self) -> dict:
        d = {
            "date": datetime.strftime(self.time, "%Y%m%d%H%M"),
            "year": str(self.time.year),
            "month": str(self.time.month),
            "day": str(self.time.day),
            "hour": str(self.time.hour),
            "minute": str(self.time.minute),
            "type": self.type,
            "station": self.station_id,
            "wind_direction": self._return_value_else_null(self.wind_dir),
            "wind_speed": self._return_value_else_null(self.wind_speed),
            "wind_gust": self._return_value_else_null(self.wind_gust),
            "visibility": self._return_value_else_null(self.vis),
            "weather_intensity": self._return_weather_else_null("+", "-", "VC"),
            "weather_description": self._return_weather_else_null("SH", "TS", "BC"),
            "weather_precipitation": self._return_weather_else_null("RA", "DZ"),
            "weather_obscuration": self._return_weather_else_null("FG", "BR"),
            "sky_layer1_cover": self._return_sky_layer_else_null(0),
            "sky_layer1_height": self._return_sky_layer_else_null(
                0, parameter="height"
            ),
            "sky_layer1_cloud": self._return_sky_layer_else_null(0, parameter="cloud"),
            "sky_layer2_cover": self._return_sky_layer_else_null(1),
            "sky_layer2_height": self._return_sky_layer_else_null(
                1, parameter="height"
            ),
            "sky_layer2_cloud": self._return_sky_layer_else_null(1, parameter="cloud"),
            "sky_layer3_cover": self._return_sky_layer_else_null(2),
            "sky_layer3_height": self._return_sky_layer_else_null(
                2, parameter="height"
            ),
            "sky_layer3_cloud": self._return_sky_layer_else_null(2, parameter="cloud"),
            "sky_layer4_cover": self._return_sky_layer_else_null(3),
            "sky_layer4_height": self._return_sky_layer_else_null(
                3, parameter="height"
            ),
            "sky_layer4_cloud": self._return_sky_layer_else_null(3, parameter="cloud"),
            "temperature": self.get_temperature(),
            "dewpoint": self.get_temperature(type="dewpoint"),
            "pressure": self.get_pressure(),
            "code": self.code.strip(),
        }
        return d
