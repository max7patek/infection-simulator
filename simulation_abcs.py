
from dataclasses import dataclass, fields, field
from enum import Enum
import math
from typing import List
from abc import ABCMeta, abstractmethod



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
        class New(cls):
            simulation = sim
        sim.__dict__[cls._name] = New 
        return New


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

