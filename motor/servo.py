import Adafruit_PCA9685
import board
import busio
import adafruit_pca9685
from time import sleep, time
import numpy as np

pwm = Adafruit_PCA9685.PCA9685()

i2c = busio.I2C(board.SCL, board.SDA)
pca = adafruit_pca9685.PCA9685(i2c)
pca.frequency = 50


class Servo:
    """
    Control the servos of the robot

    functions
    __init__
    set_pulse

    variables
    channel : int
    PCA9685 Channel (0->15)
    min : float
    Minimum servo value (0->1)
    max : float
    Maximum servo value (0->1)
    invert : bool

    """

    def __init__(self, channel, min=0, max=1, start=0, invert=False):
        self.channel = channel
        self.min = min
        self.max = max
        self.invert = invert
        self.set_pulse(start)

    def set_pulse(self, percent):
        """
        Set the duty cycle of PWM signal based on percent input

        args
        percent - float
        Number between 0->1, 0=self.min, 1=self.max
        """
        self.position = percent
        # Limit percent 0->1, invert if need be (ex/ .25 -> .75)
        pp = max(0, min(1, percent + self.invert*(1-2*percent)))
        # Convert percent 0->1 to min->max
        p = pp * (self.max - self.min) + self.min
        # Convert percent to duty cycle of PWM signal
        final = int(p * 7750) + 1220
        # Set pwm
        pca.channels[self.channel].duty_cycle = final