

from simulation import Simulation, Location, AbstractPerson
from simulation_abcs import PersonState
from collections import namedtuple
from enum import Enum
from dataclasses import dataclass, field
from random import gauss, choices, triangular
from typing import Tuple, List, Optional
from types import SimpleNamespace
import csv
import matplotlib.pyplot as plt 
from matplotlib.animation import FuncAnimation
import numpy as np


METERS_PER_DEGREE = 1852*60
AGE_RANGES=[
    ( 0,  5),
    ( 5, 10),
    (10, 15),
    (15, 20),
    (20, 25),
    (25, 30),
    (30, 35),
    (35, 40),
    (40, 45),
    (45, 50),
    (50, 55),
    (55, 60),
    (60, 65),
    (65, 70),
    (70, 75),
    (75, 80),
    (80, 85),
    (85, 90),
]

@dataclass
class UnivCentroid:
    lat: float
    lon: float
    num: int
    area: float


@dataclass
class Centroid:
    loc: Location
    num: int
    area: float
    age_range_totals: List[int]

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
    filename: str = "CharlottesvillePopulationData.csv"
    people_per_home_mean: float = 3
    people_per_home_stddev: float = 1
    campus_centroids: List[UnivCentroid] = field(default_factory=list)

    num_students_off_campus: int = 0
    include_students: bool = True

    num_people_fraction: float = 1

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
        self.width = (max_y - min_y) * METERS_PER_DEGREE

        # garauntee square
        if max_x - min_x > max_y - min_y:
            max_y = min_y + max_x - min_x
        else:
            max_x = min_x + max_y - min_y
        
        centroids = self.controids_from_rows(rows, min_x, max_x, min_y, max_y)
        if self.include_students:
            centroids.extend(self.convert_univ_centroids(self.campus_centroids, min_x, max_x, min_y, max_y))            
        else:
            pass # TODO remove off campus sutdents
            

        self.groceries.append(self.Grocery.init(Location(1, 1)))
        for centroid in centroids:
            while centroid.num > 0:
                self.Home.init(centroid)

    def remove_off_campus(self):
        for centroid in sorted(centroids):
            pass

    def convert_univ_centroids(self, univ_centroids, min_x, max_x, min_y, max_y):
        centroids = []
        for uc in univ_centroids:
            centroids.append(
                Centroid(
                    Location(
                        remap(uc.lon, min_x, max_x, 0, self.width),
                        remap(uc.lat, min_y, max_y, 0, self.width),
                    ),
                    round(uc.num * self.num_people_fraction),
                    uc.area,
                    age_range_totals=[0, 0, 0, 1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
                )
            )
        return centroids

    def controids_from_rows(self, rows, min_x, max_x, min_y, max_y):
        centroids = []
        for row in rows:
            if row.UN_2020_E:
                centroids.append(
                    Centroid(
                        Location(
                            remap(row.CENTROID_X, min_x, max_x, 0, self.width),
                            remap(row.CENTROID_Y, min_y, max_y, 0, self.width),
                        ),
                        round(row.UN_2020_E * self.num_people_fraction),
                        row.LAND_A_KM*2000,
                        age_range_totals=[
                            row.A00_04B ,
                            row.A05_09B ,
                            row.A10_14B ,
                            row.A15_19B ,
                            row.A20_24B ,
                            row.A25_29B ,
                            row.A30_34B ,
                            row.A35_39B ,
                            row.A40_44B ,
                            row.A45_49B ,
                            row.A50_54B ,
                            row.A55_59B ,
                            row.A60_64B ,
                            row.A65_69B ,
                            row.A70_74B ,
                            row.A75_79B ,
                            row.A80_84B ,
                            row.A85PLUSB,
                        ],
                    )
                )
        return centroids

    def get_xs_ys_cs(self):
        xs, ys, cs = super().get_xs_ys_cs()
        def p_to_c(p):
            if p.state in (PersonState.SICK, PersonState.ASYMPT):
                return (1, 0, 0)
            if p.state == PersonState.REMOVED:
                return (0, 0, 0)
            return (0, 1-p.age/90, p.age/90)
        return xs, ys, list(map(p_to_c, self.visible_people))


    @dataclass
    class Person(AbstractPerson):
        age: int

        @classmethod
        def init(cls, home, centroid):
            grocery_frequency = gauss(
                cls.simulation.grocery_frequency_mean, 
                cls.simulation.grocery_frequency_stddev
            )
            distancing_factor = triangular(0, 1, 0)**10
            closest_grocery = min(
                cls.simulation.groceries, 
                key=home.distance,
            )
            age_range = choices(AGE_RANGES, centroid.age_range_totals)[0]
            age = choices(list(range(*age_range)))[0]
            self = cls(
                age=age,
                home=home, 
                location=home, 
                state=PersonState.HEALTHY, 
                grocery_frequency=grocery_frequency,
                distancing_factor=distancing_factor,
                closest_grocery=closest_grocery,
            )
            self.simulation.people.append(self)
            return self


    @dataclass(unsafe_hash=True)
    class Home(Location):

        @classmethod
        def init(cls, centroid):
            num_people = round(gauss(
                cls.simulation.people_per_home_mean, 
                cls.simulation.people_per_home_stddev,
            ))
            num_people = min(num_people, centroid.num)
            centroid.num -= num_people
            noise = Location(gauss(0, centroid.area), gauss(0, centroid.area))
            loc = centroid.loc + noise
            self = cls(loc.x, loc.y)
            self.simulation.bound_loc(self)
            self.simulation.homes.append(self)
            for _ in range(num_people):
                self.simulation.Person.init(self, centroid)


    @dataclass(unsafe_hash=True)
    class Grocery(Location):
        @classmethod
        def init(cls, loc):
            self = cls(x=loc.x, y=loc.y)
            return self





if __name__ == "__main__":
    uva_pop = 16655
    campus_centroids = [
            UnivCentroid(# Gooch Dillard
                lat=38.029622,
                lon=-78.517580,
                num=round(uva_pop / 4 / 3),
                area=100,
            ),
            UnivCentroid( # Ohill
                lat=38.034270, 
                lon=-78.515764,
                num=round(uva_pop / 4 / 3),
                area=100,
            ),
            UnivCentroid(  # old dorms
                lat=38.035040, 
                lon=-78.510672,
                num=round(uva_pop / 4 / 3),
                area=100,
            ),
            UnivCentroid( # lawn
                lat=38.034533, 
                lon=-78.503991,
                num=200,
                area=100,
            ),
            UnivCentroid( # lambeth
                lat=38.041763, 
                lon=-78.504286,
                num=round(uva_pop / 4 / 3),
                area=100,
            ),
            UnivCentroid( # North Grounds
                lat=38.047359, 
                lon=-78.509730,
                num=round(uva_pop / 4 / 4),
                area=200,
            ),
        ]
    off_campus_pop = uva_pop - sum(c.num for c in campus_centroids)
    sim = NasaSimulation(
        num_people_fraction=1,
        fraction_people_show=.2,
        starting_sick=100,
        include_students=True,
        num_students_off_campus=off_campus_pop,
        campus_centroids=campus_centroids,
        grocery_frequency_mean=1/10000
    )
    sim.init()
    sim.setup_animation()
    sim.choose_initial_sick()

    anim = FuncAnimation(
        sim.fig, 
        sim.update, 
        frames=360, 
        interval=200,
        blit=True,
    )

    plt.imshow(sim.img, zorder=0,  extent=[0, sim.width, 0, sim.width])
    anim.save('sunday-with-students.mp4', fps=20, extra_args=['-vcodec', 'libx264'])
    #plt.show()
    #sim.run()

