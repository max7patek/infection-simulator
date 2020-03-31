
from dataclasses import dataclass
from enum import Enum
from typing import Tuple, List
from itertools import product
from random import random, gauss, paretovariate, uniform, choices, triangular
import math
import time

def roll(p):
    return random() < p

def _number_to_pixel(i):
    if i == 0:
        return ' '
    if i >= 10:
        return '@'
    return str(i)


class PersonState(Enum):
    HEALTHY = 1
    ASYMPT = 2
    SICK = 3
    REMOVED = 4


class SimulationComponentMeta(type):
    def __set_name__(cls, owner, name):
        cls._name = name
    def __get__(cls, obj, type=None):
        if obj is None:
            return cls
        class New(cls):
            simulation = obj
        obj.__dict__[cls._name] = New 
        return New


class SimulationComponent(metaclass=SimulationComponentMeta):
    pass


@dataclass
class Location(SimulationComponent):
    x: float
    y: float

    def distance(self, other):
        return math.hypot(self.x - other.x, self.y - other.y)
    
    def __add__(self, other):
        return Location(self.x + other.x, self.y + other.y)


@dataclass
class Simulation:
    width: int = 1000
    num_cities: int = 10
    num_homes: int = 1000
    homes_per_grocery: float = 100
    people_per_home_mean: float = 3
    people_per_home_stddev: float = 1
    city_spread: float = 100  # the std-dev of a bell curve
    city_size_alpha: float = 1  # the exponential parameter to a pareto distribution (maybe should be zipf)
    spread_radius: float = 1  # the std-dev of a bell curve
    spread_multiplier: float = 2  # multiplied with the output of the spread bell curve
    symptom_onset_p: float = 0.2  # the p of a bernoulli distribution
    recovery_p: float = 0.1  # the p of a bernoulli distribution 
    grocery_frequency_mean: float = 0.2
    grocery_frequency_stddev: float = 0.05
    time_at_grocery: int = 1
    distancing_alpha: float = 2 # the exponential parameter to a pareto law distribution
    starting_sick: int = 10
    num_trials: int = 100



    def run(self):
        self.init()
        print(self)
        self.print_state()
        for _ in range(self.num_trials):
            self.update()
            self.print_state()
            if self.asymptomatic_count + self.sick_count == 0:
                break
            #time.sleep(1)
            
    def update(self):
        for p in self.people:
            p.update()

#        infected = filter(lambda p: p.state in (PersonState.SICK, PersonState.ASYMPT), self.people)
        infected = [p for p in self.people if p.state in (PersonState.SICK, PersonState.ASYMPT)]
#        healthy = (filter(lambda p: p.state == PersonState.HEALTHY, self.people))
        healthy = [p for p in self.people if p.state == PersonState.HEALTHY]
        for i, h in product(infected, healthy):
            if h.state == PersonState.ASYMPT:
                continue
            dist = i.location.distance(h.location)
            if dist < 2:

            # infection_probability = self.spread_multiplier * gauss(0, self.spread_radius)
            # if dist < infection_probability:
                h.state = PersonState.ASYMPT

        self.fix_people_out_of_bounds()


    def init(self) -> None:
        self.people : List[self.Person] = []
        self.homes : List[self.Home] = []
        self.groceries : List[self.Grocery] = []
        self.cities : List[Location] = []
        for _ in range(self.num_cities):
            self.cities.append(self.City.from_params())
        for _ in range(round(self.num_homes / self.homes_per_grocery)):
            self.groceries.append(self.Grocery.from_params())
        for _ in range(self.num_homes):
            self.homes.append(self.Home.from_params())
            # populates people too
        self.num_people = len(self.people)
        for loc in self.homes + self.groceries:
            loc.x = max(0, min(loc.x, self.width-1))
            loc.y = max(0, min(loc.y, self.width-1))
        self.fix_people_out_of_bounds()
        initial_sick = choices(self.people, k=self.starting_sick) 
        for p in initial_sick:
            p.state = PersonState.ASYMPT

    
    @property
    def healthy_count(self):
        return sum(1 for p in self.people if p.state == PersonState.HEALTHY)
    @property
    def asymptomatic_count(self):
        return sum(1 for p in self.people if p.state == PersonState.ASYMPT)
    @property
    def sick_count(self):
        return sum(1 for p in self.people if p.state == PersonState.SICK)
    @property
    def removed_count(self):
        return sum(1 for p in self.people if p.state == PersonState.REMOVED)
        

    def fix_people_out_of_bounds(self):
        for p in self.people:
            loc = p.location
            loc.x = max(0, min(loc.x, self.width-1))
            loc.y = max(0, min(loc.y, self.width-1))
        

    def print_state(self):
        pixel_width = 100
        drawable_width = pixel_width - 2
        drawable_height = drawable_width // 2
        pixel_height = drawable_height + 2
        pixels = [[0 for __ in range(drawable_width)] for _ in range(drawable_height)]
        for p in self.people:
            loc = p.location
            row = pixels[int(loc.y / self.width * drawable_height)]
            row[int(loc.x / self.width * drawable_width)] += 1

        rows = ["".join(map(_number_to_pixel, row)) for row in pixels]
        rows = [f"|{row}|" for row in rows]
        area = "\n".join(rows)
        top_bot = f"+{''.join(['-'] * drawable_width)}+"
        stats = f"Healthy: {self.healthy_count}\tAsymptomatic: {self.asymptomatic_count}\tSick: {self.sick_count}\tRemoved: {self.removed_count}"
        print(f"{top_bot}\n{area}\n{top_bot}\n{stats}")


    def get_random_location(self) -> Location:
        return Location(x=uniform(0, self.width), y=uniform(0, self.width))

    def get_location_from_params(self) -> Location:
        city = choices(self.cities, (c.size for c in self.cities))[0]
        x = gauss(city.x, self.city_spread)
        y = gauss(city.y, self.city_spread)
        return Location(x=x, y=y)



    @dataclass
    class Person(SimulationComponent):
        location: Location
        state: PersonState
        home: Location
        closest_grocery: Location
        distancing_factor: float
        grocery_frequency: float
        

        def at_home(self) -> bool:
            return self.location == self.home

        def update(self):
            self.location = self.get_next_loc()
            if self.state == PersonState.SICK:
                if roll(self.simulation.recovery_p):
                    self.state = PersonState.REMOVED
            if self.state == PersonState.ASYMPT:
                if roll(self.simulation.symptom_onset_p):
                    self.state = PersonState.SICK
            

        def get_next_loc(self) -> Location:
            # TODO: make stay at grocery store for time_at_grocery
            if self.state in (PersonState.HEALTHY, PersonState.ASYMPT):
                if roll(self.grocery_frequency):
                    #print("Going to the grocery store")
                    return self.closest_grocery # TODO: add some area to the grocery
                if roll(self.distancing_factor):
                    #print("Not distancing")
                    return self.simulation.get_random_location()
                TURF = 2
                if self.location.distance(self.home) > TURF:
                    #print("wondered to far, returning")
                    return self.home
                return self.location + Location(gauss(0, .1), gauss(0, .1))
            else: # sick
                return self.home
            

        @classmethod
        def from_params(cls, home):
            grocery_frequency = gauss(
                cls.simulation.grocery_frequency_mean, 
                cls.simulation.grocery_frequency_stddev
            )
            #distancing_factor = paretovariate(cls.simulation.distancing_alpha)
            distancing_factor = triangular(0, 1, 0)**2
            closest_grocery = min(
                cls.simulation.groceries, 
                key=lambda g: math.hypot(g.x - home.x, g.y - home.y),
            )
            self = cls(
                home=home, 
                location=home, 
                state=PersonState.HEALTHY, 
                grocery_frequency=grocery_frequency,
                distancing_factor=distancing_factor,
                closest_grocery=closest_grocery,
            )
            return self

    @dataclass
    class Home(Location):
        @classmethod
        def from_params(cls):
            loc = cls.simulation.get_location_from_params()
            self = cls(x=loc.x, y=loc.y)
            num_people = round(gauss(
                self.simulation.people_per_home_mean, 
                self.simulation.people_per_home_stddev,
            ))
            for _ in range(num_people):
                self.simulation.people.append(self.simulation.Person.from_params(self))
            return self

    @dataclass
    class Grocery(Location):
        @classmethod
        def from_params(cls):
            loc = cls.simulation.get_location_from_params()
            self = cls(x=loc.x, y=loc.y)
            return self
                
    @dataclass
    class City(Location):
        size: int

        @classmethod
        def from_params(cls):
            x = uniform(0, cls.simulation.width)
            y = uniform(0, cls.simulation.width)
            size = paretovariate(cls.simulation.city_size_alpha)
            return cls(x=x, y=y, size=size)


sim = Simulation()
sim.run()