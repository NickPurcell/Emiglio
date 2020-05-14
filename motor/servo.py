import Adafruit_PCA9685
from time import sleep, time
import numpy as np

pwm = Adafruit_PCA9685.PCA9685()

# Don't change this!!
pwm_freq = 50
pwm.set_pwm_freq(50)


class Servo:

    def __init__(self, channel, min=0, max=1, start=0):
        self.channel = channel
        self.min = min
        self.max = max
        self.set_pulse(start)

    def set_pulse(self, percent):
        p = min(self.max, max(self.min, percent))
        final = 3850 + p * float(4040 - 3850)
        pwm.set_pwm(self.channel, int(final), 4096 - int(final))
        self.position = p
        
    def timed_pulse(self, percent, total_time):
        p = min(self.max, max(self.min, percent))
        s_pos = self.position
        delta = p - self.position
        if p == self.position:
            return True
        t_inc = total_time/(abs(delta)*409.6)
        true_start = time()
        while (delta < 0 and self.position > p) or (delta > 0 and self.position < p):
            t_start = time()
            self.set_pulse(self.position + 10/4096 + (delta < 0)*(-20/4096))
            s = t_inc - (time() - t_start)
            sleep(max(0, s))
        self.set_pulse(p)