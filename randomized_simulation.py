
from dataclasses import dataclass, field
from simulation_abcs import SimulationComponent, Location, AbstractPerson, PersonState
from simulation import Simulation
from typing import Tuple, List
from itertools import product
from random import random, gauss, paretovariate, uniform, choices, triangular
import math
import time
from tqdm import tqdm
import logging

log = logging.getLogger(__name__)

def roll(p):
    return random() < p


@dataclass
class RandomizedSimulation(Simulation):
    num_cities: int = 10
    num_homes: int = 1000
    homes_per_grocery: float = 100
    people_per_home_mean: float = 3
    people_per_home_stddev: float = 1
    city_spread: float = 100  # the std-dev of a bell curve
    city_size_alpha: float = 1  # the exponential parameter to a pareto distribution (maybe should be zipf)
    cities: List[Location] = field(default_factory=list)


    def init(self) -> None:
        super().init()
        for _ in range(self.num_cities):
            self.cities.append(self.City.init())
        for _ in range(round(self.num_homes / self.homes_per_grocery)):
            self.groceries.append(self.Grocery.init())
        log.info("Initializing People")
        for _ in self.tqdm(range(self.num_homes)):
            self.homes.append(self.Home.init())
            # populates people too
        self.num_people = len(self.people)
        for loc in self.homes + self.groceries:
            loc.x = max(0, min(loc.x, self.width-1))
            loc.y = max(0, min(loc.y, self.width-1))
        self.fix_people_out_of_bounds()

    def get_location_init(self) -> Location:
        city = choices(self.cities, (c.size for c in self.cities))[0]
        x = gauss(city.x, self.city_spread)
        y = gauss(city.y, self.city_spread)
        return Location(x=x, y=y)


    @dataclass
    class Home(Location):
        @classmethod
        def init(cls):
            loc = cls.simulation.get_location_init()
            self = cls(x=loc.x, y=loc.y)
            num_people = round(gauss(
                self.simulation.people_per_home_mean, 
                self.simulation.people_per_home_stddev,
            ))
            for _ in range(num_people):
                self.simulation.people.append(self.simulation.Person.init(self))
            return self

    @dataclass
    class Grocery(Location):
        @classmethod
        def init(cls):
            loc = cls.simulation.get_location_init()
            self = cls(x=loc.x, y=loc.y)
            return self
                
    @dataclass
    class City(Location):
        size: int

        @classmethod
        def init(cls):
            x = uniform(0, cls.simulation.width)
            y = uniform(0, cls.simulation.width)
            size = paretovariate(cls.simulation.city_size_alpha)
            return cls(x=x, y=y, size=size)


sim = RandomizedSimulation(num_homes=1000, width=1000, output_progress_bars=True)
sim.run()