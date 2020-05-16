"""
Nick Purcell

Control the servos, motors, and LED face
"""
from Emiglio.motor.mover import move_servos as move_servos, move_motors
from Emiglio.led.animate import animate
import Emiglio.led.animate
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
    with open('/home/pi/Emiglio/servo_sequence.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            s_time = time()
            move_servos('/home/pi/Emiglio/movies/{}'.format(row[0]))
            print(time()-s_time)
    move_servos('/home/pi/Emiglio/movies/reset')


def led_control():
    with open('/home/pi/Emiglio/led_sequence.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            animate('/home/pi/Emiglio/animations/{}'.format(row[0]))
        Emiglio.led.animate.stop()


def main():
    sleep(5)
    motor_thread = threading.Thread(target=motor_control)
    servo_thread = threading.Thread(target=servo_control)

    servo_thread.setDaemon(True)
    motor_thread.setDaemon(True)
    try:

        servo_thread.start()
        motor_thread.start()

        led_control()

    except KeyboardInterrupt:
        move_motors('/home/pi/Emiglio/speed/stop')
        move_servos('/home/pi/Emiglio/movies/reset')
        Emiglio.led.animate.stop()
        

    finally:
        move_motors('/home/pi/Emiglio/speed/stop')
        move_servos('/home/pi/Emiglio/movies/reset')
        Emiglio.led.animate.stop()


if __name__ == '__main__':
    main()