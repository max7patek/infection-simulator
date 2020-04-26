import csv

def get_coordinates():
    coordinates = []
    with open('CharlottesvillePopulationData.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                # print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                lat_coor = float(row[6])
                long_coor = float(row[6])
                print(f'Coordinates: {lat_coor}, {long_coor}')
                line_count += 1
                coordinates.append((lat_coor, long_coor))
                if(line_count > 10):
                    break
        print(f'Processed {line_count} lines.')
        return coordinates


print(get_coordinates())



# =================================================================

import matplotlib.pyplot as plt 
from matplotlib.animation import FuncAnimation
import numpy as np

dt = 0.005
n=20
L = 1
houses=np.zeros(n,dtype=[("position", float , 2),
                            ("velocity", float ,2),
                            ("force", float ,2),
                            ("size", float , 1)])

houses["position"]=np.random.uniform(0,L,(n,2))
houses["velocity"]=np.zeros((n,2))
houses["size"]=0.5*np.ones(n)

fig = plt.figure(figsize=(7,7))
ax = plt.axes(xlim=(0,L),ylim=(0,L))

print(houses["position"][:,0])
x = [0.40288222,0.17266386]
y = [0.5, 0.2]
scatter=ax.scatter(x, y)

def update(frame_number):
    houses["force"]=np.random.uniform(-2,2.,(n,2))
    houses["velocity"] = houses["velocity"] + houses["force"]*dt
    houses["position"] = houses["position"] + houses["velocity"]*dt

    houses["position"] = houses["position"]%L
    scatter.set_offsets(houses["position"])
    return scatter, 
    # return

anim = FuncAnimation(fig, update, interval=10)
plt.show() 