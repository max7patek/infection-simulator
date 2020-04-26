import csv

MIN_X = float('inf')
MAX_X = -float('inf')
MIN_Y = float('inf')
MAX_Y = -float('inf')

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
                long_coor = float(row[7])
                global MIN_X, MAX_X, MIN_Y, MAX_Y
                MIN_X = min(MIN_X, lat_coor)
                MAX_X = max(MAX_X, lat_coor)
                MIN_Y = min(MIN_Y, long_coor)
                MAX_Y = max(MAX_Y, long_coor)
                # print(f'Coordinates: {lat_coor}, {long_coor}')
                line_count += 1
                coordinates.append((lat_coor, long_coor))
                # if(line_count > 1000):
                #     break
        print(f'Processed {line_count} lines.')
        return coordinates

def get_x_y_data(coordinate_list):
    x_data = []
    y_data = []
    for house in coordinate_list:
        x_data.append(house[0])
        y_data.append(house[1])
    return (x_data,y_data)


# print(get_x_y_data(get_coordinates()))



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

# houses["position"]=np.random.uniform(0,L,(n,2))
# houses["velocity"]=np.zeros((n,2))
# houses["size"]=0.5*np.ones(n)

coordinate_data = get_x_y_data(get_coordinates())
house_x_data = coordinate_data[0]
house_y_data = coordinate_data[1]

fig = plt.figure(figsize=(7,7))
ax = plt.axes(xlim=(MIN_X,MAX_X),ylim=(MIN_Y,MAX_Y))

# print(houses["position"][:,0])

scatter=ax.scatter(house_x_data, house_y_data)

def update(frame_number):
    # houses["force"]=np.random.uniform(-2,2.,(n,2))
    # houses["velocity"] = houses["velocity"] + houses["force"]*dt
    # houses["position"] = houses["position"] + houses["velocity"]*dt

    # houses["position"] = houses["position"]%L
    # scatter.set_offsets(houses["position"])
    # return scatter, 
    return

anim = FuncAnimation(fig, update, interval=10)
plt.show() 