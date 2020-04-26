

from simulation import Simulation, Location
from collections import namedtuple
from dataclasses import dataclass, field
from random import gauss
from typing import Tuple, List
from types import SimpleNamespace
import csv


#Centroid = namedtuple("Centroid", ["loc", "num", "density"])

@dataclass
class Centroid:
    loc: Location
    num: int
    area: float

def _process_row(line, headers):
    def _process_pair(pair):
        key, val = pair
        if any(key.endswith(x) for x in ("_KM", "_X", "_Y", "_DS")):
            val = float(val)
        else:
            try:
                val = int(val)
            except ValueError:
                pass
        return (key, val)
    return map(_process_pair, zip(headers, line))


def remap(old, old_min, old_max, new_min, new_max):
    return (((old - old_min) * (new_max - new_min)) / (old_max - old_min)) + new_min


@dataclass
class NasaSimulation(Simulation):
    filename: str = ""
    people_per_home_mean: float = 3
    people_per_home_stddev: float = 1

    def init(self):
        assert self.filename, "Must supply population data csv filename"
        super().init()
        with open(self.filename) as file:
            reader = csv.reader(file)
            headers = next(reader)

            rows = [
                SimpleNamespace(**dict(_process_row(line, headers))) 
                for line in reader
            ]
        max_x = max(row.CENTROID_X for row in rows)
        min_x = min(row.CENTROID_X for row in rows)
        max_y = max(row.CENTROID_Y for row in rows)
        min_y = min(row.CENTROID_Y for row in rows)
        print(f"({max_y}, {max_x}), ({min_y}, {min_x}) ")

        # garauntee square
        if max_x - min_x > max_y - min_y:
            max_y = min_y + max_x - min_x
        else:
            max_x = min_x + max_y - min_y
        
        centroids = []
        for row in rows:
            if row.UN_2020_E:
                centroids.append(
                    Centroid(
                        Location(
                            remap(row.CENTROID_X, min_x, max_x, 0, self.width),
                            remap(row.CENTROID_Y, min_y, max_y, 0, self.width),
                        ),
                        row.UN_2020_E,
                        row.LAND_A_KM,
                    )
                )

        self.groceries.append(self.Grocery.init(Location(1, 1)))
        for centroid in centroids:
            while centroid.num > 0:
                num_people = round(gauss(
                    self.people_per_home_mean, 
                    self.people_per_home_stddev,
                ))
                num_people = min(num_people, centroid.num)
                centroid.num -= num_people
                noise = Location(gauss(0, 1/centroid.density), gauss(0, centroid.density))
                home = self.Home.init(centroid.loc + noise, num_people)
                self.bound_loc(home)
                self.homes.append(home)


    @dataclass
    class Home(Location):
        @classmethod
        def init(cls, loc, num_people):
            self = cls(x=loc.x, y=loc.y)
            for _ in range(num_people):
                self.simulation.people.append(self.simulation.Person.init(self))
            return self

    @dataclass
    class Grocery(Location):
        @classmethod
        def init(cls, loc):
            self = cls(x=loc.x, y=loc.y)
            return self





if __name__ == "__main__":
    sim = NasaSimulation(filename="CharlottesvillePopulationData.csv", output_progress_bars=True)
    sim.run()

