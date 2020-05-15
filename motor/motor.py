import RPi.GPIO as GPIO
import board
import busio
import adafruit_pca9685
from time import sleep, time

i2c = busio.I2C(board.SCL, board.SDA)
pca = adafruit_pca9685.PCA9685(i2c)
pca.frequency = 50

GPIO.setmode(GPIO.BCM)

GPIO.setwarnings(False)


class Motor:

    def __init__(self, dir_pin, pwm_channel, flip=False):
        self.dir_pin = dir_pin
        self.pwm_channel = pwm_channel
        # Set initial direction and speed (fwd, 0)
        GPIO.setup(dir_pin, GPIO.OUT, initial=GPIO.HIGH)
        pca.channels[self.pwm_channel].duty_cycle = 0
        self.dir = 1
        self.speed = 0
        self.flip = flip
        
    def set_speed(self, speed):
        if -1 <= speed <= 1:
            self.speed = speed
            self.dir = (speed >= 0) #^ self.flip
            GPIO.output(self.dir_pin, self.dir)
            pca.channels[self.pwm_channel].duty_cycle = int(abs(speed)*0xffff)
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
        pca.channels[self.pwm_channel].duty_cycle = 0
        sleep(.1)
        
        
        
def main():
    motor_1 = Motor(29,15)
    motor_2 = Motor(31,14)
    motor_3 = Motor(33,13)
    motor_4 = Motor(37,12)


if __name__ == "__main__":
    main()