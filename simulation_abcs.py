
from dataclasses import dataclass
from enum import Enum
import math

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



class Person(SimulationComponent):
    pass

@dataclass
class Location(SimulationComponent):
    x: float
    y: float

    def distance(self, other):
        return math.hypot(self.x - other.x, self.y - other.y)
    
    def __add__(self, other):
        return Location(self.x + other.x, self.y + other.y)

