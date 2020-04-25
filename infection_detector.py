
from typing import List, Union, Optional
from dataclasses import dataclass, field
from random import shuffle
from simulation_abcs import Location, AbstractPerson, PersonState
from itertools import product
from random import gauss


@dataclass
class Node:
    representative: AbstractPerson
    children: List[Optional["Node"]]
    child_index: int = 0

    def full(self):
        return bool(self.children[-1])

    def find_partition(self, p):
        """Assumes self is full!"""
        return min(
            self.children, 
            key=lambda c: c.representative.location.distance(p.location)
        )

    def push_back(self, p, num_children):
        self.children[self.child_index] = Node(p, [None] * num_children)
        self.child_index += 1

    def pockets(self, stack=None):
        stack = stack or []
        if not self.full():
            yield [c.representative for c in self.children if c] + stack
        else:
            stack.append(self.representative)
            for child in self.children:
                yield from child.pockets(stack)
            stack.pop()

    def find_pocket(self, p, stack=None):
        stack = stack or []
        if not self.full():
            yield from [c.representative for c in self.children if c] + stack
        else:
            stack.append(self.representative)
            child = self.find_partition(p)
            yield from child.find_pocket(p, stack)
            stack.pop()
                
        


def detect(simulation):
    """

    """
    shuffle(simulation.people)
    nonremoved = (
        p for p in simulation.people
        if p.state != PersonState.REMOVED
    )
#    people_iter = iter(nonremoved)
    root = Node(next(nonremoved), [None] * simulation.maximum_gathering)
    for p in simulation.tqdm(
        nonremoved, 
        total=len(simulation.people) - simulation.removed_count-1
    ):
        node = root
        while node.full():
            node = node.find_partition(p)
        node.push_back(p, simulation.maximum_gathering)

    to_be_sick = []
    for pocket in simulation.tqdm(list(root.pockets())):
        infected = (
            p for p in pocket
            if p.state in (PersonState.SICK, PersonState.ASYMPT)
        )
        healthy = (p for p in pocket if p.state == PersonState.HEALTHY)
        for i, h in product(infected, healthy):
            dist = i.location.distance(h.location)
            infection_probability = abs(
                simulation.spread_multiplier * gauss(
                    0, simulation.spread_radius
                )
            )
            if dist < infection_probability:
                to_be_sick.append(h)
    return to_be_sick

            


def smart_detect(simulation):
    """Faster, but doesn't implement large gathering bans"""
    shuffle(simulation.people)
    infected = [
        p for p in simulation.people
        if p.state in (PersonState.SICK, PersonState.ASYMPT)
    ]
    people_iter = iter(infected)
    root = Node(next(people_iter), [None] * simulation.maximum_gathering)
    for p in simulation.tqdm(
        people_iter, 
        total=simulation.asymptomatic_count+ simulation.sick_count-1
    ):
        node = root
        while node.full():
            node = node.find_partition(p)
        node.push_back(p, simulation.maximum_gathering)

    to_be_sick = []
    healthy = [p for p in simulation.people if p.state == PersonState.HEALTHY]
    for p in simulation.tqdm(healthy):
        for i in root.find_pocket(p):
            dist = i.location.distance(p.location)
            infection_probability = abs(
                simulation.spread_multiplier * gauss(
                    0, simulation.spread_radius
                )
            )
            if dist < infection_probability:
                to_be_sick.append(p)
    return to_be_sick
