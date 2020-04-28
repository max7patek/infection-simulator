from nasa_simulation import NasaSimulation, UnivCentroid
import matplotlib.pyplot as plt 
from matplotlib.animation import FuncAnimation
from datetime import datetime
import os
import sys

uva_pop = 16655
uva_center = (38.033736, -78.509330)
campus_centroids = [
        UnivCentroid( # Gooch Dillard
            lat=38.029622,
            lon=-78.517580,
            num=round(uva_pop / 4 / 3),
            area=120,
        ),
        UnivCentroid( # Ohill
            lat=38.034270, 
            lon=-78.515764,
            num=round(uva_pop / 4 / 3),
            area=120,
        ),
        UnivCentroid(  # old dorms
            lat=38.035040, 
            lon=-78.510672,
            num=round(uva_pop / 4 / 3),
            area=120,
        ),
        UnivCentroid( # lawn
            lat=38.034533, 
            lon=-78.503991,
            num=round(uva_pop / 4 / 5),
            area=120,
        ),
        UnivCentroid( # lambeth
            lat=38.041763, 
            lon=-78.504286,
            num=round(uva_pop / 4 / 5),
            area=80,
        ),
        UnivCentroid( # North Grounds
            lat=38.047359, 
            lon=-78.509730,
            num=round(uva_pop / 4 / 4),
            area=200,
        ),
    ]
groceries = [
    (38.053540, -78.500610), #Kroger
    (38.059880, -78.491700), #Kroger
    (38.009030, -78.500500), #Wegmans
    (38.013140, -78.502760), #Food Lion
    (38.0014282, -78.4964649), #Food Lion
    (38.029985281465876, -78.45825010512779), #Food Lion
    (38.097245, -78.4671279), #Walmart
    (38.0596895, -78.4892307), #Whole Foods
    (38.0500364,-78.5042732), #Harris Teeter
    (38.0629873, -78.4914987), #Trader Joe’s
]

on_campus_pop = sum(c.num for c in campus_centroids)
off_campus_pop = uva_pop - on_campus_pop


if __name__ == "__main__":
    LIVE = False
    # print(f"{uva_pop=}, {off_campus_pop=}, {on_campus_pop=}")
    # with_studs = NasaSimulation(num_people_fraction=1,
    #     fraction_people_show=.2,
    #     starting_sick=1000,
    #     include_students=True,num_students_off_campus=off_campus_pop,
    #     campus_centroids=campus_centroids,
    #     university_centroid=uva_center,
    #     output_state=False,
    #     grocery_coords=groceries,
    #     output_progress_bars=True,)
    # without_studs = NasaSimulation(num_people_fraction=1,
    #     fraction_people_show=.2,
    #     starting_sick=1000,
    #     include_students=False,num_students_off_campus=off_campus_pop,
    #     campus_centroids=campus_centroids,
    #     university_centroid=uva_center,
    #     output_state=False,
    #     grocery_coords=groceries,
    #     output_progress_bars=True,)
    # with_studs.init()
    # without_studs.init()
    # print(f"{len(with_studs.people)=}, {len(without_studs.people)=}")

    params = dict(
        num_people_fraction=1,
        fraction_people_show=.2,
        starting_sick=0.1,
        include_students=True,
    )
    sim = NasaSimulation(
        num_students_off_campus=off_campus_pop,
        campus_centroids=campus_centroids,
        university_centroid=uva_center,
        output_state=False,
        grocery_coords=groceries,
        output_progress_bars=False,
        **params
    )
    sim.init()
    sim.setup_animation()
    sim.choose_initial_sick()

    anim = FuncAnimation(
        sim.fig, 
        sim.update, 
        frames=1000, 
        interval=200,
        blit=True,
    )
    plt.imshow(sim.img, zorder=0,  extent=[0, sim.width, 0, sim.width])

    if not LIVE:
        parms_str = ",".join(f"{key}={val}" for key, val in params.items())
        filename = f"runs/{parms_str}; {datetime.now()}"
        os.mkdir(filename)

    if not LIVE:
        try:
            anim.save(f'{filename}/animation.mp4', fps=10, extra_args=['-vcodec', 'libx264'])
        except StopIteration:
            pass
        plt.clf()
    else:
        plt.show()



    if len(sim.r_t)%2: # odd
        sim.r_t.pop()

    daily_rs = [
        (a + b) / 2 for a, b in zip(
            sim.r_t[0::2],
            sim.r_t[1::2],
        )
    ]
    plt.plot(daily_rs)
    plt.xlabel("days")
    plt.ylabel("R")
    plt.title("Reproductive Number Over Time")
    if not LIVE:
        plt.savefig(f"{filename}/R_t.png")
        plt.clf()
    else:
        plt.show()

    if len(sim.new_cases_t)%2: # odd
        sim.new_cases_t.pop()

    daily_new_cases = [
        a + b for a, b in zip(
            sim.new_cases_t[0::2],
            sim.new_cases_t[1::2],
        )
    ]
    plt.plot(daily_new_cases)
    plt.xlabel("days")
    plt.ylabel("new cases")
    plt.title("New Cases Per Day Over Time")
    if not LIVE:
        plt.savefig(f"{filename}/new_cases.png")
        plt.clf()
    else:
        plt.show()
    
    
    if not LIVE:
        otherstats_file = open(f"{filename}/stats.py", "w")
    else:
        otherstats_file = sys.stdout
    deaths = sum(1 for p in sim.people if p.dead)
    print(f"{deaths=}", file=otherstats_file)
    

    

