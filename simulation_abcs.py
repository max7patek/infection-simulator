
from dataclasses import dataclass, fields, field, make_dataclass
from enum import Enum
import math
from typing import List
from abc import ABCMeta, abstractmethod
from functools import lru_cache


class PersonState(Enum):
    HEALTHY = 1
    ASYMPT = 2
    SICK = 3
    REMOVED = 4


class SimulationComponentMeta(ABCMeta):

    def __set_name__(cls, owner, name):
        cls._name = name
    def __get__(cls, sim, type=None):
        if sim is None:
            return cls
        bases = (cls,) + tuple(
            getattr(sup, cls._name) 
            for sup in sim.__class__.__bases__ 
            if hasattr(sup, cls._name)
        )
        new_type = make_dataclass(
            cls._name, 
            (("simulation", AbstractSimulation, sim),), 
            bases=bases,
            unsafe_hash=any(issubclass(b, Location) for b in bases), 
        )
        sim.__dict__[cls._name] = new_type
        return new_type


class SimulationComponent(metaclass=SimulationComponentMeta):

    def update(self, *args, **kwargs):
        pass

    @classmethod
    @abstractmethod
    def init(self, *args, **kwargs):
        pass


class AbstractPerson(SimulationComponent):
    pass

@dataclass
class Location(SimulationComponent):
    x: float
    y: float

    @classmethod
    def init(cls, x, y):
        return cls(x, y)

    def distance(self, other):
        return math.hypot(self.x - other.x, self.y - other.y)
    
    def __add__(self, other):
        return Location(self.x + other.x, self.y + other.y)


class AbstractSimulation(metaclass=ABCMeta):
    pass
