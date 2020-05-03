#!/usr/bin/env python3
# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.
 
import time
from neopixel import *
import argparse
import numpy as np
from math import pi, cos
 
# LED strip configuration:
LED_COUNT      = 256      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 25     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
 
 
 # Make every LED sparkle 
sparkle = np.random.permutation(np.arange(-2*pi/.2, 2*pi/.2, 4*pi/(.2*256)))
spark_add = np.random.permutation(np.arange(pi/14, pi/24, (pi/24-pi/14)/256))
 
 
# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)
 
def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, color)
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)
 
def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)
 
def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i+j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)
 
def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)
 
def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, wheel((i+j) % 255))
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)
 
def fire(strip, wait_ms=30):
    global sparkle, spark_add
    max_decay = 1/7
    min_decay = 1/16
    fire = np.zeros((16,16))
    fire = np.ones((16,16))*np.array(((1,),(1,),(1,),(1,),
                                      (0,),(0,),(0,),(0,),
                                      (0,),(0,),(0,),(0,),
                                      (0,),(0,),(0,),(0,)))
    mul = 100
    c_time = time.time()
    while True:
        fire = np.roll(fire, 1, axis=0)
        fire[0] = np.random.rand((16))*.2+.7
        r_2_l = True
        sparkle = sparkle + spark_add
        for i in range(0,16):
            for j in range(0,16):
                if i != 0:
                    fire[i,j] -= ((max_decay - min_decay)*np.random.rand(1)+min_decay)
                    #if fire[i][j] != 0:
                    fire[i,j] += sum(fire[i-1,max(0,j-1):min(16,j+2)])/mul
                    if i != 15:# and fire[i][j] != 0:
                        fire[i,j] += sum(fire[i+1,max(0,j-1):min(16,j+2)])/mul
                    if j != 0:# and fire[i][j] != 0:
                        fire[i,j] += sum(fire[max(0,i-1):min(16,i+2),j-1])/mul
                    fire[i,j] = min(1, fire[i,j])
                if 1 >= fire[i][j] > 2/3:
                    r = 200
                    g = 200
                    b = min(200, max(0, (fire[i][j] - 2/3)* 200 * 3))
                elif 2/3 >= fire[i,j] > 1/3:
                    r = 200
                    g = min(200, max(0, (fire[i][j] - 1/3)* 200 * 3))
                    b = 0
                elif 1/3 >= fire[i][j] > 0:
                    r = min(200, max(0, (fire[i][j])* 200 * 3))
                    g = 0
                    b = 0
                else:
                    r = 0
                    g = 0
                    b = 0
                if 6 > time.time() - c_time > 3:
                    old = {'r' : r,'g' : g,'b' : b}
                    r = old['g']
                    g = old['b']
                    b = old['r']
                elif 9 > time.time() - c_time > 6:
                    old = {'r' : r,'g' : g,'b' : b}
                    r = old['b']
                    g = old['r']
                    b = old['g']
                elif 12 > time.time() - c_time > 9:
                    old = {'r' : r,'g' : g,'b' : b}
                    r = old['b']
                    g = old['g']
                    b = old['r']
                elif time.time() - c_time > 12:
                    c_time = time.time()
                if r_2_l:
                    if not r == 0:
                        r += max(0,50*r/200*cos(sparkle[(15-i)*16+j]))
                    if not g == 0:
                        g += max(0,50*g/200*cos(sparkle[(15-i)*16+j]))
                    if not b == 0:
                        b += max(0,50*b/200*cos(sparkle[(15-i)*16+j]))
                    strip.setPixelColor((15-i)*16+j,Color(int(g),int(r),int(b)))
                else:
                    if not r == 0:
                        r += max(0,50*r/200*cos(sparkle[(15-i-1)*16-j]))
                    if not g == 0:
                        g += max(0,50*g/200*cos(sparkle[(15-i-1)*16-j]))
                    if not b == 0:
                        b += max(0,50*b/200*cos(sparkle[(15-i-1)*16-j]))
                    strip.setPixelColor((15-i+1)*16-j-1,Color(int(g),int(r),int(b)))
            r_2_l = not r_2_l
        strip.show()
        time.sleep(wait_ms/1000)
        
         
     
 
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
 
    print ('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')
 
    try:
 
        while True:
            #print ('Theater chase animations.')
            #theaterChase(strip, Color(127, 127, 127))  # White theater chase
            #theaterChase(strip, Color(127,   0,   0))  # Red theater chase
            #theaterChase(strip, Color(  0,   0, 127))  # Blue theater chase
            #print ('Rainbow animations.')
            #rainbow(strip)
            #rainbowCycle(strip)
            #theaterChaseRainbow(strip)
            fire(strip)
 
    except KeyboardInterrupt:
        colorWipe(strip, Color(0,0,0), 0)
