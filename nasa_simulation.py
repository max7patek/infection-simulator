

from simulation import Simulation, Location
from collections import namedtuple
from dataclasses import dataclass, field
from typing import Tuple, List
from types import SimpleNamespace
import csv
import matplotlib.pyplot as plt 
from matplotlib.animation import FuncAnimation
import numpy as np

Centroid = namedtuple("Centroid", ["loc", "num"])

def _process_row(line, headers):
    def _process_pair(pair):
        key, val = pair
        if key.endswith("_KM") or key.endswith("_X") or key.endswith("_Y"):
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
    centroids: List[Centroid] = field(default_factory=list)

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
        
        for row in rows:
            if row.UN_2020_E:
                self.centroids.append(
                    Centroid(
                        Location(
                            remap(row.CENTROID_X, min_x, max_x, 0, self.width),
                            remap(row.CENTROID_Y, min_y, max_y, 0, self.width),
                        ),
                        row.UN_2020_E,
                    )
                )
        self.groceries.append(self.Grocery.init(Location(1, 1)))
        for centroid in self.centroids:
            self.homes.append(self.Home.init(centroid.loc, 1))

#         last = None
#         for row in sorted(rows, key=lambda row: row.CENTROID_X):
# #            print(f"{row.CENTROID_X:.5f}, {row.CENTROID_Y:.5f}")
#             if last:
#                 print(f"{row.CENTROID_X - last.CENTROID_X:.5f}")
#             last = row

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
    #anim.save('animation.mp4', writer = 'ffmpeg', fps=30)
    plt.show()
    #sim.run()

