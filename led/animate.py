# Nick Purcel
#
# Create animations on WS2812 16x16 LED screen
import time
from neopixel import *
import argparse
from PIL import Image
import os
import numpy as np
import csv
from math import pi, cos
import threading
from random import seed
from random import random

seed(time.time())
 
# LED strip configuration:
LED_COUNT      = 256      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 25       # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
 
# Make every LED sparkle 
sparkle = np.random.permutation(np.arange(-2*pi/.2, 2*pi/.2, 4*pi/(.2*256)))
spark_add = np.random.permutation(np.arange(pi/14, pi/24, (pi/24-pi/14)/256))

pix_val = np.zeros([256,3])

 # Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """ 
    Go through each LED one by one and change color
    
    Arguements
    strip : Adafruit_NeoPixel
    Output strip
    color: Color
    Output color
    wait_ms : float
    time to wait between changes
    """
    
    # Iterate through each LED, change pixel color, and wait
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)
 
def animate(ani_name):
    """ 
    Go through each image in animation folder and display
    
    Arguements
    ani_name : String
    Name of animation folder
    """
    global pix_val
    t_last = time.time()
    timing = []
    with open(ani_name + '/info.csv', newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
    data_cache = ()
    for dat in data:
        if dat == ['0','0']:
            data_cache = ()
            continue
        elif dat[0] == '0':
            if dat[1][0] == 'r':
                reps = int(random()*float(dat[1][1:]))
            else:
                reps = int(dat[1])-1
            for i in range(reps):
                for p in data_cache:
                    im = Image.open(ani_name + '/' + p[1] + '.png').convert("RGB")
                    im_data = im.getdata()
                    pix_val = np.array(im_data)
                    if p[0][0] == 'r':
                        t_hold = random()*float(p[0][1:])
                    else:
                        t_hold = float(p[0])
                    time.sleep(max(t_hold - (time.time() - t_last), 0))
                    t_last = time.time()
            data_cache = ()
            continue
        im = Image.open(ani_name + '/' + dat[1] + '.png').convert("RGB")
        im_data = im.getdata()
        data_cache = data_cache + (dat, )
        pix_val = np.array(im_data)
        if dat[0][0] == 'r':
            t_hold = random()*float(dat[0][1:])
        else:
            t_hold = float(dat[0])
        time.sleep(max(t_hold - (time.time() - t_last), 0))
        t_last = time.time()
        
def ani_timer(fps, timer_lock, stop_lock):
    start_timer = threading.Timer(1/fps,draw,args=(timer_lock,))
    start_timer.start()
    while True:
        event_in_wating = timer_lock.wait()
        event_in_wating = stop_lock.wait()
        timer_lock.clear()
        timer = threading.Timer(1/fps,draw,args=(timer_lock,))
        timer.start()
    
def draw(timer_lock):
    global pix_val
    timer_lock.set()
    r_2_l = True
    for i in range(16):
        for j in range(16):
            if not r_2_l:
                if any(pix_val[i*16 + j]):
                    spark = 1/(2*pi) + 1/pi*(1+cos(.2*sparkle[i+j])+cos(.2*2*sparkle[i+j])+cos(.2*3*sparkle[i+j])+cos(.2*4*sparkle[i+j])+cos(.2*5*sparkle[i+j]))
                    spark_mult = 20
                    color_out = Color(int(max(min(pix_val[i*16 + j][1] + spark_mult*spark, 255), 0)),
                    int(max(min(pix_val[i*16 + j][0] + spark_mult*spark, 255), 0)), int(max(min(pix_val[i*16 + j][2] + spark_mult*spark, 255), 0)))
                else:
                    color_out = Color(0,0,0)
                strip.setPixelColor(i*16 + j, color_out)
            else:
                strip.setPixelColor((i+1)*16 - 1 - j, Color(int(pix_val[i*16 + j][1]), int(pix_val[i*16 + j][0]), int(pix_val[i*16 + j][2])))
        r_2_l = not r_2_l
    strip.show()
    
def sparkle_control():
    global sparkle
    while True:
        s_time = time.time()
        sparkle = sparkle + spark_add
        time.sleep(max(1/16 - (time.time() - s_time), 0))
    
 
# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()
 
    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()
 
    timer_lock = threading.Event()
    timer_lock.clear()
    
    stop_lock = threading.Event()
    stop_lock.set()
    
    draw_thread = threading.Thread(name='ani_timer', target=ani_timer, args=(16, timer_lock, stop_lock))
    sparkle_thread = threading.Thread(name='sparkle_control', target=sparkle_control)

    draw_thread.setDaemon(True)
    sparkle_thread.setDaemon(True)
    
    draw_thread.start()
    sparkle_thread.start()
    
    try:
 
        while True:
            print("Talking")
            for i in range(0,3):
                animate('blank_talk')
            print("Blank")
            for i in range(0,1):
                animate('blank_face')
            #for i in range(0,10):
            #    animate('mad', 32)
 
    except KeyboardInterrupt:
        stop_lock.clear()
        colorWipe(strip, Color(0,0,0), 0)
