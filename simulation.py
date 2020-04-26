
from dataclasses import dataclass, fields, field
import math
from typing import List
from abc import ABCMeta, abstractmethod
import infection_detector
from random import random, gauss, paretovariate, uniform, choices, triangular
from simulation_abcs import AbstractPerson, Location, PersonState, SimulationComponent
from tqdm import tqdm

import matplotlib.pyplot as plt 
from matplotlib.animation import FuncAnimation
import numpy as np
# from scipy.misc import imread

def _number_to_pixel(i):
    if i == 0:
        return ' '
    if i >= 10:
        return '@'
    return str(i)

def roll(p):
    return random() < p


@dataclass
class Simulation(metaclass=ABCMeta):
    # containers
    people: List[AbstractPerson] = field(default_factory=list)
    homes: List[Location] = field(default_factory=list)
    groceries: List[Location] = field(default_factory=list)

    # disease spread
    spread_radius: float = .75  # the std-dev of a bell curve
    symptom_onset_p: float = 0.2  # the p of a bernoulli distribution
    recovery_p: float = 0.1  # the p of a bernoulli distribution 
    starting_sick: int = 10

    # behaviors
    maximum_gathering: int = 10  # the number of children per node in space partitioning algorithm
    grocery_frequency_mean: float = 1/28
    grocery_frequency_stddev: float = 1/14
    time_at_grocery: int = 1
    distancing_alpha: float = 2  # the exponential parameter to a pareto law distribution

    # parameters
    num_trials: int = 100
    output_state: bool = True
    output_progress_bars: bool = True
    width: int = 1000


    @abstractmethod
    def init(self, *args, **kwargs):
        if self.output_progress_bars:
            self.tqdm = tqdm
        else:
            self.tqdm = lambda iterable, *args, **kwargs: iterable


    def setup_animation(self):
        self.img = plt.imread("cville.png")
        self.fig = plt.figure()
        self.fig.set_dpi(100)
        self.fig.set_size_inches(7, 6.5)
        ax = plt.axes(xlim=(0,self.width),ylim=(0,self.width))
        xs = [p.location.x for p in self.people]
        ys = [p.location.y for p in self.people]
        self.scatter=ax.scatter(xs, ys)

    def choose_initial_sick(self):
        initial_sick = choices(self.people, k=self.starting_sick) 
        for p in initial_sick:
            p.state = PersonState.ASYMPT

    def run(self):
        self.init()
        self.setup_animation()
        self.choose_initial_sick()
        self.print_state()
        for _ in range(self.num_trials):
            self.update()
            if self.asymptomatic_count + self.sick_count == 0:
                break

    def update(self, _):
        for field in fields(self):
            attr = getattr(self, field.name)
            if isinstance(attr, list) and attr and isinstance(attr[0], SimulationComponent):
                for comp in attr:
                    comp.update()
        to_be_sick = infection_detector.detect(self)
        for p in to_be_sick:
            p.state = PersonState.ASYMPT
        self.fix_people_out_of_bounds()
        if self.output_state:
            self.print_state()

        xs = [p.location.x for p in self.people]
        ys = [p.location.y for p in self.people]
        self.scatter.set_offsets(np.c_[xs, ys])
        print(np.c_[xs, ys])
        return self.scatter,  

    
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


    @dataclass
    class Person(AbstractPerson):
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
        def init(cls, home):
            grocery_frequency = gauss(
                cls.simulation.grocery_frequency_mean, 
                cls.simulation.grocery_frequency_stddev
            )
            #distancing_factor = paretovariate(cls.simulation.distancing_alpha)
            distancing_factor = triangular(0, 1, 0)**2
            closest_grocery = min(
                cls.simulation.groceries, 
                key=home.distance,
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


