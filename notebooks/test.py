import time
from math import sin, cos
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D      

x_value = 0
x_list = []
y1_list = []
y2_list = []

props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
plt.rcParams['animation.html'] = 'jshtml'
fig, (ax1, ax2) = plt.subplots(2,1)
ax1.set_title("Power supply parameters")
ax1.set(ylabel='Voltage [V]')
ax2.set(xlabel='sample [n]', ylabel='Current [A]')
ax1.set_ylim(-1.5, 1.5)
ax2.set_ylim(-1.5,1.5)
ax1.grid(1)
ax2.grid(1)

line1 = Line2D([0],[0.0],color='blue')
ax1.add_line(line1)
line2 = Line2D([0],[0.0],color='red')
ax2.add_line(line2)


box1 = ax1.text(.87, 0.95, str(0), transform=ax1.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)
box2 = ax2.text(0.87, 0.95, str(0), transform=ax2.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)

def annotate(last_y1, last_y2):
    box1.set_text(str(round(last_y1,3)))
    box2.set_text(str(round(last_y2,3)))

def data_gen(x_value):
    x_value = round(x_value,3)
    total_1 = round(sin(x_value),3)
    total_2 = round(cos(x_value),3)
    return (x_value,total_1,total_2)

def run(i):
    global x_value ,x_list,y1_list, y2_list
    x, y1, y2 = data_gen(x_value)
    x_value += 0.2
    
    if len(x_list) <=200:
        x_list.append(x)
        y1_list.append(y1)
        y2_list.append(y2)
    else:
        x_list.append(x)
        x_list.pop(0)
        y1_list.append(y1)
        y1_list.pop(0)
        y2_list.append(y2)
        y2_list.pop(0) 

    ax1.set_xlim(left=max(0, x_list[-1] - 20), right=x_list[-1] + 10)
    ax2.set_xlim(left=max(0, x_list[-1] - 20), right=x_list[-1] + 10)

    line1.set_data(x_list,y1_list)
    line2.set_data(x_list,y2_list)
    annotate(y1_list[-1], y2_list[-1])

ani = FuncAnimation(fig, run, interval=1)
plt.show()