import Adafruit_PCA9685
import time
from time import sleep

pwm = Adafruit_PCA9685.PCA9685()

# Don't change this!!
pwm_freq = 50
pwm.set_pwm_freq(50)

position = [0, 0]
pwm.set_pwm(0, 4096, 0)

def wave():
    while True:
        pwm.set_pwm(0, 4058, 38)
        sleep(.5)
        pwm.set_pwm(0, 3809, 287)
        sleep(.5)


def set_position(percent, duration):
    if percent > 1:
        print('Percent must be <= 1')
        return
    final = 3850 + percent * float(4040 - 3850)
    delta = final - position[0]
    step_size = delta/(duration*20)
    print('Delta: {} Step: {}'.format(delta, step_size))
    while abs(final - position[0]) <= step_size or (step_size < 0) == (final - position[0] < 0):
        s_time = time.time()
        position[0] += step_size
        posint = int(position[0])
        pwm.set_pwm(0, posint, 4096 - posint)
        sleep(max(0, .05 - (time.time() - s_time)))
    position[0] = int(final)
    pwm.set_pwm(0, int(final), 4096- int(final))


def set_pulse(percent, channel):
    final = 3850 + percent * float(4040 - 3850)
    pwm.set_pwm(channel, int(final), 4096 - int(final))
    position[channel] = int(final)
