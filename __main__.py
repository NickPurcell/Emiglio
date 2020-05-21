"""
Nick Purcell

Control the servos, motors, and LED face
"""
from Emiglio.motor.mover import move_servos as move_servos, move_motors
from Emiglio.led.led_control import Screen
from Emiglio.motor.mover import Servo_Controller
from time import time, sleep
import threading
import csv

def motor_control():
    with open('/home/pi/Emiglio/motor_sequence.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            move_motors('/home/pi/Emiglio/speed/{}'.format(row[0]))
    move_motors('/home/pi/Emiglio/speed/stop')


def servo_control():
    s_control = Servo_Controller()
    s_control.start()


def led_control():
    face = Screen()
    face.start()


def main():
#    sleep(5)
#    motor_thread = threading.Thread(target=motor_control)
#    servo_thread = threading.Thread(target=servo_control)

#    servo_thread.setDaemon(True)
#    motor_thread.setDaemon(True)
    try:

        servo_control()

        led_control()
        while True:
            sleep(10)

    except KeyboardInterrupt:
        move_motors('/home/pi/Emiglio/speed/stop')
        move_servos('/home/pi/Emiglio/movies/reset')
        

    finally:
        move_motors('/home/pi/Emiglio/speed/stop')
        move_servos('/home/pi/Emiglio/movies/reset')


if __name__ == '__main__':
    main()