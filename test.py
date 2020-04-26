import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.misc import imread


img = imread("image.png")

fig = plt.figure()
# fig.set_dpi(100)
# fig.set_size_inches(7, 6.5)

ax = plt.axes(xlim=(-20, 40), ylim=(-20, 40))
patch = plt.Circle((5, -5), 0.75, fc='r')


def init():
    patch.center = (40, 40)
    ax.add_patch(patch)
    return patch,

def animate(i):
    x = 10 + 3 * np.sin(np.radians(i))
    y = 10 + 3 * np.cos(np.radians(i))
    patch.center = (x, y)
    return patch,

anim = animation.FuncAnimation(fig, animate, 
                               init_func=init, 
                               frames=360, 
                               interval=20,
                               blit=True)

plt.imshow(img,zorder=0,  extent=[-20, 40.0, -20.0, 40.0])
# anim.save('the_movie.mp4', writer = 'ffmpeg', fps=30)
plt.show()