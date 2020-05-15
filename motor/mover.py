"""
Nick Purcell

Move the servo based on "movie" csv files in /Emiglio/movies
"""
import servo
import threading
import servo
from time import sleep, time
import csv
import numpy as np

r_s = servo.Servo(0,start=0)
r_e = servo.Servo(1,min=.4,max=.9,start=.5,invert=True)
r_w = servo.Servo(2,start=.4)
l_s = servo.Servo(3,start=0,invert=True)
l_e = servo.Servo(4,min=.1,max=.53,start=.6)
l_w = servo.Servo(5,start=.4)

servos = (r_s, r_e, r_w, l_s, l_e, l_w)


def move(movie_name, move_freq=100):
    """ 
    Move servos based on csv
    CSV organized with 1 instruction per row
    (R Shoulder) (R Elbow) (R Wrist) (L Shoulder) L Elbow) L Wrist) (Move Time)

    Designed to make smooth, slowed down movements rather than jerky movements
    By just switching PWM and waiting
    
    Arguements
    movie_name : String
    Name of movie csv
    move_freq : int
    Frequency in Hz of moves by servo - default(100)
    """
    # Get current servo position
    current = [r_s.position , r_e.position, r_w.position, l_s.position, l_e.position, l_w.position]
    instructs = ()
    # Read csv data
    with open(movie_name + '.csv', newline='') as f:
        reader = csv.reader(f)
        data = np.array(list(reader)).astype(float)
    # Cache all instructions for each move before begining movie
    for row in data:
        final = row[0:6]
        t_time = row[6]
        num_moves = int(t_time * move_freq)
        delta = np.subtract(final, current) / num_moves
        for i in range(num_moves):
            instructs = instructs + (np.add(current, delta), )
            current += delta 
    # Iterate through each instruction
    for instruct in instructs:
        # Save begining of move for timing
        t_start = time()
        # move each servo to newest position
        positions = instruct
        for i, s in enumerate(servos):
            s.set_pulse(positions[i])
        # Sleep until begining of next move cycle
        stime = max(0, 1/move_freq-time() + t_start)
        sleep(stime)

