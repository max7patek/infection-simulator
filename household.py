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
import random
from scipy.misc import imread


img = imread("cville.png")

fig = plt.figure()
fig.set_dpi(100)
fig.set_size_inches(7, 6.5)

coordinate_data = get_x_y_data(get_coordinates())
house_x_data = coordinate_data[0]
house_y_data = coordinate_data[1]

ax = plt.axes(xlim=(MIN_X,MAX_X),ylim=(MIN_Y,MAX_Y))


scatter=ax.scatter(house_x_data, house_y_data)

def animate(i):
    global house_x_data, house_y_data
    house_y_data = [i + random.uniform(-.001, .001) for i in house_y_data]

    scatter.set_offsets(np.c_[house_x_data, house_y_data])
    return scatter, 

anim = FuncAnimation(fig, animate, 
                               frames=360, 
                               interval=200,
                               blit=True)

plt.imshow(img,zorder=0,  extent=[MIN_X, MAX_X, MIN_Y, MAX_Y])
# anim.save('animation.mp4', writer = 'ffmpeg', fps=30)
plt.show()

