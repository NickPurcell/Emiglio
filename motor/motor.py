import RPi.GPIO as GPIO
import Adafruit_PCA9685
from time import sleep, time

pwm = Adafruit_PCA9685.PCA9685()

pwm_freq = 50
pwm.set_pwm_freq(50)

GPIO.setmode(GPIO.BCM)

GPIO.setwarnings(False)


class Motor:

    def __init__(self, dir_pin, pwm_channel):
        self.dir_pin = dir_pin
        self.pwm_channel = pwm_channel
        # Set initial direction and speed (fwd, 0)
        GPIO.setup(dir_pin, GPIO.OUT, initial=GPIO.HIGH)
        pwm.set_pwm(pwm_channel, 0, 4096)
        self.dir = 1
        self.speed = 0
        
    def set_speed(self, speed):
        if -1 <= speed <= 1:
            self.speed = speed
            self.dir = speed >= 0
            GPIO.output(self.dir_pin, self.dir)
            if speed == 0:
                s = abs(speed)*.5+.5
            else:
                s = ((abs(speed)-1e-15)*.5+.5)
            pwm.set_pwm(self.pwm_channel, int(4096*(1-s)), int(4096*s))
            sleep(.1)
        else:
           print("Speed {} Invalid, -1 <= Speed <= 1".format(speed))
           return
            
    def change_dir(self, dir):
        self.dir = dir > 0
        GPIO.output(self.dir_pin, self.dir)
        
    def change_dir_pin(self, dir_pin):
        self.dir_pin = dir_pin
        GPIO.setup(dir_pin, GPIO.OUT, initial=self.dir)
        
    def stop(self):
        pwm.set_pwm(self.pwm_channel, int(4096/2), int(4096/2))
        sleep(.1)
        
        
        
def main():
    motor_1 = Motor(29,15)
    motor_2 = Motor(31,14)
    motor_3 = Motor(33,13)
    motor_4 = Motor(37,12)


if __name__ == "__main__":
    main()