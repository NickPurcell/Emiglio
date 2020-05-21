# Nick Purcel
#
# Create animations on WS2812 16x16 LED screen
import time
from neopixel import *
from PIL import Image
import numpy as np
import csv
from math import pi, cos
import threading
from random import seed, random

# Use start time as random seed
seed(time.time())
 
# LED strip configuration:
LED_COUNT      = 256      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 25       # Set to 0 for darkest and 255 for brightest - THIS SHOULD BE LOW <50
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
 
# Make every LED sparkle 
sparkle = np.random.permutation(np.arange(-2*pi/.2, 2*pi/.2, 4*pi/(.2*256)))
spark_add = np.random.permutation(np.arange(pi/14, pi/24, (pi/24-pi/14)/256))
 
 
pix_for = np.zeros([256,3])
pix_bak = np.zeros([256,3])


#Very Slow don't use
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
    global pix_for
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
                    pix_for = np.array(im_data)
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
        pix_for = np.array(im_data)
        if dat[0][0] == 'r':
            t_hold = random()*float(dat[0][1:])
        else:
            t_hold = float(dat[0])
        time.sleep(max(t_hold - (time.time() - t_last), 0))
        t_last = time.time()
        

def ani_timer(fps, timer_lock, stop_lock, for_black = False):
    """
    Use timer to refresh the screen at ((fps))

    Args
    fps : float
    Frames per second desired
    Timer_Lock : threading.Event
    Event to hold the timer until new frame is being drawn
    stop_lock : threading.Event
    Stop drawing new frames if the program has been stopped
    """
    start_timer = threading.Timer(1/fps,draw,args=(timer_lock, for_black))
    start_timer.start()
    while True:
        event_in_wating = timer_lock.wait()
        event_in_wating = stop_lock.wait()
        timer_lock.clear()
        timer = threading.Timer(1/fps,draw,args=(timer_lock, for_black))
        timer.start()
    
	
def draw(timer_lock, for_black):
    """
	Set colors on board based on pix_val and effects
	
	Args
	timer_lock : threading.Event
	Event to hold the timer until new frame is being drawn
	"""
    global pix_for, pix_bak
    # Begin the timer for a new frame when each frame begins
    timer_lock.set()
    # Toggle right to left and left to right to match LED strip
    r_2_l = True
    # Iterate through each pixel
    for i in range(0,16):
        for j in range(0,16):
            if i == j == 0:
                r_2_l == True
            # Toggle draw direction
            if r_2_l:
                index = (i+1)*16 - 1 - j
            else:
                index = i*16 + j
            # Calculate sparkle based on first few terms of Delta fourier expansion
            spark = 1/(2*pi) + 1/pi*(1+cos(.2*sparkle[index])+cos(.2*2*sparkle[index])+
                                       cos(.2*3*sparkle[index])+cos(.2*4*sparkle[index])+
                                       cos(.2*5*sparkle[index]))
            spark_mult = 20
            # Draw foreground over background
            if not for_black:
                r, g, b = pix_for[index]
                if not any((r, g, b)):
                    r, g, b = pix_bak[index]
            # Draw background and make foreground black
            else:
                r, g, b = pix_bak[index]
                if any(pix_for[index]):
                    r, g, b = (0, 0, 0)
            if any((r, g, b)):
                r += spark_mult*spark
                g += spark_mult*spark
                b += spark_mult*spark
            color_out = Color(int(max(min(g, 255), 0)),
                              int(max(min(r, 255), 0)),
                              int(max(min(b, 255), 0)))
            strip.setPixelColor(i*16 + j, color_out)
        r_2_l = not r_2_l
    strip.show()
    
def fire(wait_ms=30):
    """
    Background animation - Fire
    
    Pixels generated at bottom row with variable brightness
    Move pixel row up one row of LEDs each update frame
    Decrease pixel brightness by random amount each update
    Increase pixel brightness based on brightness of nearby pixels
    
    Args
    Output : Numpy.Array
    Array to update
    """
    global pix_bak
    # Set max and min decay amounts, higher -> higher flame
    max_decay = 1/8
    min_decay = 1/17
    # Initialize fire array, set bottom to zero to create a bit of an "explosion"
    fire = np.zeros((16,16))
    fire = np.ones((16,16))*np.array(((1,),(1,),(1,),(1,),
                                      (0,),(0,),(0,),(0,),
                                      (0,),(0,),(0,),(0,),
                                      (0,),(0,),(0,),(0,)))
    # Multiplier to to set amount by which pixel is effected by other pixels                                  
    mul = 100
    while True:
        # Move pixels up the screen by rolling the array
        fire = np.roll(fire, 1, axis=0)
        # Set bottom row
        fire[0] = np.random.rand((16))*.2+.7
        # Iterate through each pixel to change output array
        for i in range(0,16):
            for j in range(0,16):
                # Increase the brightness of each pixel based on brightness of surrounding pixels
                if i != 0:
                    fire[i,j] -= ((max_decay - min_decay)*np.random.rand(1)+min_decay)
                    fire[i,j] += sum(fire[i-1,max(0,j-1):min(16,j+2)])/mul
                    if i != 15:
                        fire[i,j] += sum(fire[i+1,max(0,j-1):min(16,j+2)])/mul
                    if j != 0:
                        fire[i,j] += sum(fire[max(0,i-1):min(16,i+2),j-1])/mul
                    fire[i,j] = min(1, fire[i,j])
                # Decrease color vals based on brightness, change color order for diff. colored flames
                # r - g - b = Natural
                # b - r - g = Cool purple
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
                pix_bak[(15-i)*16+j] = int(r),int(g),int(b)
        time.sleep(wait_ms/1000)


def wiper(delay=.1):
    global pix_bak
    for i in range(256):
        pix_bak[i] = (255,0,0)
    colors = ((255,0,0),
              (255,75,0),
              (255,255,0),
              (0,255,0),
              (0,100,255),
              (50,0,255),
              (255,0,255))
    current = (255,0,0)
    while True:
        for i in range(7):
            next = (i != 6) * (i+1)
            color_tran = np.subtract(colors[next], colors[i])/5
            current = colors[i]
            for j in range(5):
                
                current = np.add(current, color_tran)
                pix_bak = np.roll(pix_bak, 16, axis = 0)
                pix_bak[0:16] = current*np.ones((16,3))
                time.sleep(delay)
            current = colors[next]
            for j in range(6):
                pix_bak = np.roll(pix_bak, 16, axis = 0)
                pix_bak[0:16] = current*np.ones((16,3))
                time.sleep(delay)

def stop():
    global stop_lock, timer_lock
    stop_lock.clear()
    timer_lock.clear()
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0,0,0))
    strip.show()
                
            


def sparkle_control():
    """
    Manage Sparkle Effect
    """
    global sparkle
    while True:
        s_time = time.time()
        sparkle = sparkle + spark_add
        time.sleep(max(1/16 - (time.time() - s_time), 0))
    
# Start Neopixel
# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
# Intialize the library (must be called once before other functions).
strip.begin()

timer_lock = threading.Event()
timer_lock.clear()

stop_lock = threading.Event()
stop_lock.set()

draw_thread = threading.Thread(name='ani_timer', target=ani_timer, 
                               args=(16,  timer_lock, stop_lock, True))
fire_thread = threading.Thread(name='wiper', target=wiper)
sparkle_thread = threading.Thread(name='sparkle_control', target=sparkle_control)

draw_thread.setDaemon(True)
sparkle_thread.setDaemon(True)
fire_thread.setDaemon(True)

draw_thread.start()
sparkle_thread.start()
fire_thread.start()
