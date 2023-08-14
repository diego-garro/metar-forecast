from typing import List

from pydantic import BaseModel


class Station(BaseModel):
    name: str
    icao: str


class Stations:
    def __init__(self):
        self.mroc = Station(name="Aeropuerto Int. Juan Santamaría", icao="mroc")
        self.mrlb = Station(name="Aeropuerto Int. Daniel Oduber", icao="mrlb")
        self.mrpv = Station(name="Aeropuerto Int. Tobías Bolaños", icao="mrpv")
        self.mrlm = Station(name="Aeropuerto Int. de Limón", icao="mrlm")

        self._count = 0
        self._list = [self.mroc, self.mrpv, self.mrlb, self.mrlm]

    def __iter__(self):
        return self

    def __next__(self):
        if self._count >= len(self._list):
            raise StopIteration

        current = self._list[self._count]
        self._count += 1
        return current

    def __getitem__(self, subscript):
        if isinstance(subscript, slice):
            return self._list.__getitem__(subscript)
        return None

    def __len__(self):
        return len(self._list)

    @property
    def items(self) -> List[Station]:
        return self._list


if __name__ == "__main__":
    stations = Stations()
    for stn in stations[2:]:
        print(stn)
