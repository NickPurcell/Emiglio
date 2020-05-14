from time import sleep
import servo

r_s = servo.Servo(0, start=1)
r_e = servo.Servo(1, min=0, max=.6, start=0)
r_w = servo.Servo(2, start = .6)
l_s = servo.Servo(3, start=0)
l_e = servo.Servo(4, min=.4, max=1, start=1)
l_w = servo.Servo(5, start = .4)
