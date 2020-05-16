# Nick Purcell - UWT 2020
# Control RC car with dual shock 4 controller
# (Right trigger forward, left trigger backwards, left thumbstick direction)
# import motor control script
import motor
from motor import Motor
import threading
import math
# import evdev
from evdev import InputDevice, categorize, ecodes
from time import sleep

moto_fr = Motor(13,14, True)
moto_fl = Motor(5,15, True)
moto_br = Motor(26,12)
moto_bl = Motor(6,13)

# Speed information
speed_right = 0
speed_left = 0
speed_forward = 0
speed_reverse = 0
val = 0
# creates object gamepad
gamepad = InputDevice('/dev/input/event2')
# prints out device info at start
print(gamepad)
# Give it some time to get everything set up
sleep(2)

def set_speed(spd_r, spd_l):
    moto_br.set_speed(spd_r)
    moto_bl.set_speed(spd_l)
    moto_fr.set_speed(spd_r)
    moto_fl.set_speed(spd_l)

# Control speed of rover
def speed_control():
    global speed_right, speed_left, speed_forward, speed_reverse
    while True:
        # Stop if both triggers pressed
        if speed_forward > 0 and speed_reverse > 0:
            motor.stop()
        else:
            # Set forward speed based on triggers and thumbstick
            speed_right = -val + (speed_forward - speed_reverse)
            speed_left = val + (speed_forward - speed_reverse)
            # Saturate speed
            if abs(speed_right) > 255:
                speed_right = math.copysign(255, speed_right)
            if abs(speed_left) > 255:
                speed_left = math.copysign(255, speed_left)
            #print('Fwd: {} Rev: {}'.format(speed_forward, speed_reverse))
            print('L: {} R: {}'.format(speed_left, speed_right))
            set_speed(speed_right/255, speed_left/255)

t = threading.Thread(name='speed_control', target=speed_control)
t.start()

# Get gamepad input in a loop
for event in gamepad.read_loop():
    # buttons
    if event.type == ecodes.EV_KEY:
        print(categorize(event))
        print(event.code)
    # Analog inputs
    if event.type == ecodes.EV_ABS:
        if(event.code == 0):
            val = (event.value - 128) * 4
            # Dead zone
            if abs(val) < 60:
                val = 0
            # Saturate val
            if abs(val) > 510:
               val = math.copysign(510, val)
        # Get forward and reverse speed from triggers
        if event.code == 5:
            speed_forward = event.value
        if event.code == 2:
             speed_reverse = event.value
