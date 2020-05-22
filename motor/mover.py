"""
Nick Purcell

Move the servo based on "movie" csv files in /Emiglio/movies
"""
from Emiglio.motor.servo import Servo
from Emiglio.motor.motor import Motor
from threading import Thread, Event
from time import sleep, time
import csv
import numpy as np

r_s = Servo(0,start=0)
r_e = Servo(1,min=.4,max=.9,start=.5,invert=True)
r_w = Servo(2,start=.4)
l_s = Servo(3,start=0,invert=True)
l_e = Servo(4,min=.1,max=.53,start=.6)
l_w = Servo(5,start=.4)
        
r_f = Motor(13,14)
r_b = Motor(26,12)
l_f = Motor(5,15)
l_b = Motor(6,13)

servos = (r_s, r_e, r_w, l_s, l_e, l_w)
motors = (r_f, r_b, l_f, l_b)

class Servo_Controller(Thread):
    def __init__(self, move_freq=30):
        # Thread initialization
        super(Servo_Controller, self).__init__()
        self.setDaemon(True)
        self.run_flag = Event()
        self.run_flag.set()
        
        self.move_freq = move_freq
        
        # Cache data
        self.instructs = ()
        current = [r_s.position , r_e.position, r_w.position, l_s.position, l_e.position, l_w.position]
        with open('/home/pi/Emiglio/servo_sequence.csv', newline='') as f:
            sequence = csv.reader(f)
            sequ = ('reset', )
            for row in sequence:
                sequ = sequ + ((row[0]), )
            sequence = sequ + (('reset'), )
            # Iterate through each animation
            ind = 0
            move_indexes = ()
            for row in sequence:
                with open('/home/pi/Emiglio/movies/{}.csv'.format(row), newline='') as g:
                    movie_list = np.array(list(csv.reader(g))).astype(float)
                    for row in movie_list:
                        final = row[0:6]
                        t_time = row[6]
                        delta = np.subtract(final, current) / num_moves
                        move_indexes = move_indexes + (ind, )
                        for i in range(num_moves):
                            self.instructs = self.instructs + (np.add(current, delta), )
                            current += delta

    def run(self):
        # Iterate through each instruction
        for instruct in self.instructs:
            wait = self.run_flag.wait()
            # Save begining of move for timing
            t_start = time()
            # move each servo to newest position
            positions = instruct
            for i, s in enumerate(servos):
                s.set_pulse(positions[i])
            # Sleep until begining of next move cycle
            etime = time() - t_start
            stime = max(0, 1/self.move_freq-etime)
            sleep(max(0, 1/self.move_freq-(time() - t_start)))


def move_motors(mots_name, move_freq=5):
    """ 
    Control motor speed based on csv
    CSV organized with 1 instruction per row
    (R Front) (R Back) (L Front) (L Back) (Transition time)
    
    Arguements
    mots_name : String
    Name of control csv
    move_freq : int
    Frequency in Hz of moves by servo - default(100)
    """
    # Get current servo position
    current = [r_f.speed, l_f.speed, r_b.speed, l_b.speed,]
    instructs = ()
    # Read csv data
    with open(mots_name + '.csv', newline='') as f:
        reader = csv.reader(f)
        data = np.array(list(reader)).astype(float)
    # Cache all instructions for each move before begining movie
    for row in data:
        final = row[0:4]
        t_time = row[4]
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
        speed = instruct
        for i, s in enumerate(motors):
            s.set_speed(speed[i])
        # Sleep until begining of next move cycle
        stime = max(0, 1/move_freq-time() + t_start)
        sleep(stime)


def move_servos(movie_name, move_freq=30):
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
    t = 0
    e = 0
    for instruct in instructs:
        # Save begining of move for timing
        t_start = time()
        # move each servo to newest position
        positions = instruct
        for i, s in enumerate(servos):
            s.set_pulse(positions[i])
        # Sleep until begining of next move cycle
        etime = time() - t_start
        stime = max(0, 1/move_freq-etime)
        t += stime
        e += etime
        sleep(stime)
