import servo
import threading
from time import sleep, time
import csv
import numpy as np

r_s = servo.Servo(0, start=1)
r_e = servo.Servo(1,0,.6,0)
r_w = servo.Servo(2,start=.6)
l_s = servo.Servo(3, start=0)
l_e = servo.Servo(4,.4,1,1)
l_w = servo.Servo(5,start=.6)

servos = (r_s, r_e, r_w, l_s, l_e, l_w)
pulses = [r_s.position , r_e.position, r_w.position, l_s.position, l_e.position, l_w.position]

move_freq = 100
    
    
def set_pulses(calc_lock):
    """
    This function controls the timing of the animations
    Args:
    calc_lock - threading.Event
    Wait to calculate next move until set
    """
    global pulses, servos
    while True:
        # Save begining of animation for timing
        t_start = time()
        # move each servo to newest position
        for i, s in enumerate(servos):
            s.set_pulse(pulses[i])
        # Begin next calculation
        calc_lock.set()
        # Sleep until begining of next animation cycle
        stime = max(0, 1/move_freq-time() + t_start)
        sleep(stime)
    
    
def animate(ani_name, calc_lock):
    """ 
    Move servos based on csv
    CSV organized with 1 instruction per row
    (R Shoulder) (R Elbow) (R Wrist) (L Shoulder) L Elbow) L Wrist) (Move Time)
    
    Arguements
    ani_name : String
    Name of animation csv
    calc_lock - threading.Event
    Wait to calculate next move until set
    """
    global pulses
    # Read csv data
    with open(ani_name + '.csv', newline='') as f:
        reader = csv.reader(f)
        data = np.array(list(reader)).astype(float)
    
    # Cache data before begining animations
    instructs = (pulses, )
    for row in data:
        final = row[0:6]
        final[3:5] = np.subtract([1,1], final[3:5])
        # Convert final from 0-1 to servo.min->servo.max
        for i, servo in enumerate(servos):
            final[i] = final[i]*(servo.max - servo.min) + servo.min
        final = tuple(final)
        start = (instructs[len(instructs)-1])
        delta = np.subtract(final, start) * 1/(row[6]* move_freq)
        for i in range(int(row[6]*move_freq)):
            instructs = instructs + (np.add(instructs[len(instructs)-1], delta), )
    # Iterate through each instruction
    for instruct in instructs:
        event_in_waiting = calc_lock.wait()
        calc_lock.clear()
        pulses = (instruct)

sleep(2)

calc_lock = threading.Event()
calc_lock.set()

pulse_thread = threading.Thread(target=set_pulses, args=(calc_lock,))

pulse_thread.setDaemon(True)

pulse_thread.start()

for i in range(0,10):
    animate('simple_dance', calc_lock)

animate('reset', calc_lock)

