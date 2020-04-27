
from dataclasses import dataclass, fields, field
import math
from typing import List
from abc import ABCMeta, abstractmethod
import infection_detector
from random import random, gauss, paretovariate, uniform, choices, triangular
from simulation_abcs import AbstractPerson, Location, PersonState, SimulationComponent, AbstractSimulation
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
class Simulation(AbstractSimulation):
    # containers
    people: List[AbstractPerson] = field(default_factory=list)
    homes: List[Location] = field(default_factory=list)
    groceries: List[Location] = field(default_factory=list)

    # disease spread
    spread_radius: float = .75  # the std-dev of a bell curve
    symptom_onset_p: float = 1/10  # the p of a bernoulli distribution
    recovery_p: float = 1/30  # the p of a bernoulli distribution 
    starting_sick: int = 10

    # behaviors
    maximum_gathering: int = 10  # the number of children per node in space partitioning algorithm
    grocery_frequency_mean: float = 1/14
    grocery_frequency_stddev: float = 1/14
    random_walk_stddev: float = 5
    random_walk_limit: float = 1000
    distancing_exp: float = 6  # the exponent of distancing willingness, higher is more distancing

    # parameters
    num_trials: int = 100
    output_state: bool = True
    output_progress_bars: bool = True
    fraction_people_show: float = 0.1
    width: int = 1000


    @abstractmethod
    def init(self, *args, **kwargs):
        if self.output_progress_bars:
            self.tqdm = tqdm
        else:
            self.tqdm = lambda iterable, *args, **kwargs: iterable


    def get_xs_ys_cs(self):
        xs = [p.location.x for p in self.visible_people]
        ys = [p.location.y for p in self.visible_people] 
        cs = [(1, 0, 0,) for p in self.visible_people]
        return xs, ys, cs

    def setup_animation(self):
        self.img = plt.imread("cville.png")
        self.fig = plt.figure()
        self.fig.set_dpi(100)
        self.fig.set_size_inches(7, 6.5)
        ax = plt.axes(xlim=(0,self.width),ylim=(0,self.width))
        self.visible_people = [p for p in self.people if random() < self.fraction_people_show]
        xs, ys, cs = self.get_xs_ys_cs()
        self.scatter=ax.scatter(xs, ys, s=1, c=cs)

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
            self.update(None)
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

        xs, ys, cs = self.get_xs_ys_cs()
        self.scatter.set_offsets(np.c_[xs, ys])
        self.scatter.set_color(cs)
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
        

    def bound_loc(self, loc):
        loc.x = max(0, min(loc.x, self.width-1))
        loc.y = max(0, min(loc.y, self.width-1))

    def fix_people_out_of_bounds(self):
        for p in self.people:
            self.bound_loc(p.location)
        

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
            self.location.update()
            self.location = self.get_next_loc()
            if self.state == PersonState.SICK:
                if roll(self.simulation.recovery_p):
                    self.state = PersonState.REMOVED
            if self.state == PersonState.ASYMPT:
                if roll(self.simulation.symptom_onset_p):
                    self.state = PersonState.SICK
            

        def get_next_loc(self) -> Location:
            if self.state in (PersonState.HEALTHY, PersonState.ASYMPT):
                if roll(self.grocery_frequency):
                    return self.closest_grocery # TODO: add some area to the grocery
                if roll(self.distancing_factor):
                    return self.simulation.get_random_location()
                if self.location.distance(self.home) > self.simulation.random_walk_limit:
                    return self.home
                walk_noise = Location(
                    gauss(0, self.simulation.random_walk_stddev), 
                    gauss(0, self.simulation.random_walk_stddev),
                )
                return self.location + walk_noise
            else: # sick
                return self.home
            

        @classmethod
        def init(cls, home):
            grocery_frequency = gauss(
                cls.simulation.grocery_frequency_mean, 
                cls.simulation.grocery_frequency_stddev
            )
            distancing_factor = triangular(0, 1, 0)**self.simulation.distancing_exp
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


