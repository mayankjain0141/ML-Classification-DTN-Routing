#!/usr/bin/python
"""
 trace2one.py
 Read the raw mobility trace file and generate a trace file in ns-2
 format.  As we only have one zebra data (#8), we need to generate other
 zebras' movement using the distribution data of #8.

 We use relative metrics to create the group trace as follows:
 (i) moving distance
 (ii) direction change
 They are both relative metrics.
 We do not use dx, dy because we need to create the movement of each
 individual zebra instead of duplicating a zebra movement.  There are
 randomness issues to consider, which are addressed in the code.

 Usage: trace2one.py baseoutUTM1.txt <filenum>
 Example: to create a group of 10 zebras, call
 'trace2one.py baseoutUTM1.txt 10'; 10 single node mobility traces names
 baseoutUTM.n0 - baseoutUTM.n9 will be created.  Use cat to put them
 together should create a single trace file that can be read by ONE.
"""

import string
import re
import sys
import os
import math
import random

x_pos_n = []
y_pos_n = []
time_n = []
z_pos_n = []

def print_help_and_exit():
    ''' Print a help message and exits '''
    print(__doc__)
    sys.exit()  # Standard way to exit a python script
    return

def get_delta_xy(filename):
    ''' Reads through filename and extracts the delta movement for x, y '''

    file = open(filename, 'r')
    dist_list = []
    direct_list = []
    ln = 0
    for line in file.readlines():
        ln += 1
        x1, y1 = extract_position(line)
        if ln > 1:
            distance = math.sqrt((x1-x0)**2+(y1-y0)**2)
            dist_list.append(distance)
            direction = math.atan2(y1-y0, x1-x0)
            direct_list.append(direction)
        x0, y0 = x1, y1  # save x & y
    file.close()
    return dist_list, direct_list

def extract_position(line):
    ''' Extracts the position data from the raw data line  '''
    words = line.split()
    x = eval(words[9])  # We know ahead of time this is the right one
    x /= 6
    y = eval(words[10])
    y /= 6
    return x, y

# Group trace can be created using two approaches:
# (i) d_direct[i] always corresponds to d_distance[i]
# (ii) or using some random combination

def get_delta_direction(direct_list):
    ''' Calculate the delta direction '''
    dd = []
    for i in range(len(direct_list)):
        if i > 0:
            dd.append(direct_list[i]-direct_list[i-1])
    return dd

def write_ns_trace(dist_list, dd, filename, filenum):
    ''' Write the ONE-ns2 trace file '''
    max_speed = 0
    min_speed = 100

    file = open("input.txt", 'w')
    # Format - startTime endTime minX maxX minY maxY minZ maxZ
    file.write("0 56000 0 1000 0 1000 0 0\n")
    # choosing a random offset for the location record times
    offset = random.uniform(0, 200)
    for i in range(eval(filenum)):
        start_pos_x = random.uniform(0, 1000)
        start_pos_y = random.uniform(0, 1000)
        start_pos_z = 0
        start_dir = random.uniform(0, 2*math.pi)
        
        x_pos_n.append(start_pos_x)
        y_pos_n.append(start_pos_y)
        z_pos_n.append(start_pos_z)
        
        current_x = start_pos_x
        current_y = start_pos_y
        current_direction = start_dir

        temp = 0
        file.write('%f %d %f %f\n' % (temp, i, current_x, current_y))

        for move in range(100*len(dist_list)):
            if(temp > 56000):
                break
            move_distance = random.choice(dist_list)
            
            # moving by choosing a random element 
            # from the extracted distances and directions
            next_x = current_x + move_distance * math.cos(current_direction)
            next_y = current_y + move_distance * math.sin(current_direction)

            # need some tweaks for 8-min intervals, which is shown in the raw data file
            # this is just an approximation
            speed = move_distance / 8
            max_speed = max(max_speed, speed)
            min_speed = min(min_speed, speed)
            
            # boundary conditions
            ovrflow = 0
            if next_x > 1000:
                ovrflow = next_x - 1000
                next_x = 1000 - ovrflow
            if next_x < 0:
                next_x *= -1
            if next_y > 1000:
                ovrflow = next_y - 1000
                next_y = 1000 - ovrflow
            if next_y < 0:
                next_y *= -1
              
            temp += offset
            file.write('%f %d %f %f\n' % (temp, i, next_x, next_y))
            time_n.append(temp)
            x_pos_n.append(next_x)
            y_pos_n.append(next_y)
            current_direction += random.choice(dd)

    file.close()
    print(max_speed)
    print(min_speed)
    return

def make_ext_filename(filename, n):
    ''' Replace file by file.extn '''
    new_fn = filename.replace("txt", "n"+str(n))
    return new_fn

def main():
    if len(sys.argv) < 3:
        print_help_and_exit()

    filename = sys.argv[1]
    filenum = sys.argv[2]

    # Get the template position trace from filename
    distance_list, direction_list = get_delta_xy(filename)

    # Get the direction difference list from direction_list
    dd_list = get_delta_direction(direction_list)

    # Duplicate movement pattern into other node movement trace
    write_ns_trace(distance_list, dd_list, filename, filenum)
    x_pos_n.sort()
    y_pos_n.sort()
    z_pos_n.sort()
    time_n.sort()
    print("X: ", x_pos_n[0], x_pos_n[-1])
    print("Y: ", y_pos_n[0], y_pos_n[-1])
    print("Z: ", z_pos_n[0], z_pos_n[-1])
    print("Time: ", time_n[0], time_n[-1])


if __name__ == '__main__':
    main()
