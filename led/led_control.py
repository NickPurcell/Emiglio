"""
Nick Purcell

Screen is master control class

LED Effect is template class for all LED Effects

"""
from time import time, sleep
from neopixel import *
from PIL import Image
import numpy as np
import csv
from math import pi, cos
from threading import Thread, Event
from random import seed, random
 
class Screen(Thread):
    def __init__(self, mask=True, invert=False):
        super(Screen, self).__init__()
        # LED strip configuration
        LED_COUNT      = 256      # Number of LED pixels.
        LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
        LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
        LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
        LED_BRIGHTNESS = 25       # Set to 0 for darkest and 255 for brightest - THIS SHOULD BE LOW <50
        LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
        LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
        
        # Initialize NeoPixel strip
        self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        self.strip.begin()
        
        # Run in the background
        self.setDaemon(True)
        
        self.run_flag = Event()
        self.run_flag.set()
        
        self.mask = mask
        self.invert = invert
        
        self.image_list = (['cool','cool_a', .1], )
        with open('/home/pi/Emiglio/led_sequence.csv', newline='') as f:
            reader = csv.reader(f)
            for ani in reader:
                with open('/home/pi/Emiglio/animations/' + ani[0] + '/info.csv', newline='') as g:
                    g_reader = csv.reader(g)
                    for row in g_reader:
                        self.image_list = self.image_list + ([ani[0], row[1], row[0]], )
        self.index = 0


    def run(self):
        """
        
        Each effect follows generally the same process
         - thread initializes, flag set
         - thread waits for effect start event set
         - process data
         - set ready event when effect array ready
         - if flag set, main thread waits for effect data
        """
        #~~~~~Initializaiton~~~~~
        # Store time of next image, effect, or sparkle cycle
        next_im = 0
        next_effect = 0
        next_spark = 0
        # Image processing initialization
        im = Image.open('/home/pi/Emiglio/animations/' + self.image_list[self.index][0] + '/' + self.image_list[self.index][1] + '.png').convert("RGB")
        image = np.array(im.getdata())
        self.index += 1
        next_im = time() + float(self.image_list[self.index][2])
        
        # Draw thread
        draw_thread = LED_Draw(self.strip)
        
        # Sparkle thread
        sparkle_frequency = 15
        
        sparkle_init = np.random.permutation(np.arange(-2*pi/.2, 2*pi/.2, 4*pi/(.2*256)))
        sparkle_add = np.random.permutation(np.arange(pi/14, pi/24, (pi/24-pi/14)/256))
        
        sparkle_thread = Sparkle(sparkle_frequency, [sparkle_add, 20], sparkle_init)
        
        # Effect
        effect_frequency = 10
        
        # Fire
        fire_init = np.ones((16,16))*np.array(((1,),(1,),(1,),(1,),
                                               (0,),(0,),(0,),(0,),
                                               (0,),(0,),(0,),(0,),
                                               (0,),(0,),(0,),(0,)))
                                                     
        #effect_thread = Fire(effect_frequency, [1/8, 1/17, 100], fire_init)
        
        t_last = time()
        
        # Rainbow
        colors = ((255,0,0),
                  (255,75,0),
                  (255,255,0),
                  (0,255,0),
                  (0,100,255),
                  (50,0,255),
                  (255,0,255))
        current = (255,0,0)
        color_index = 0
        trans_index = 0
        color_tran = 0
        next = (255, 0, 0)
        
        effect_thread = Rainbow_Wipe(effect_frequency, [colors, current, color_index, trans_index, color_tran, next])
        
        new_screen = np.zeros((256,3))
        effect = np.zeros((256,3))
        sparkle = np.zeros((256,3))
        
        # Loop
        while self.run_flag.wait():
            # Draw the screen at the beggining of the loop
            new_screen[np.nonzero(new_screen)[0]] = np.add(new_screen[np.nonzero(new_screen)[0]], np.dot(sparkle[np.nonzero(new_screen)[0]].reshape((-1,1)), np.ones((1,3))))

            draw_thread.screen = new_screen
            draw_thread.draw_event.set()
            last_draw = time()
            
            #Set Flags to begin effect threads in background
            # Sparkle processing
            if time() >= next_spark:
                next_spark = last_draw + 1/sparkle_thread.frequency
                sparkle_thread.run_flag.set()
            
            # Effect processing
            if time() >= next_effect:
                next_effect = last_draw + 1/effect_thread.frequency
                effect_thread.run_flag.set()
                
            # Image processing
            if time() >= next_im:
                if self.index >= len(self.image_list):
                    break
                im = Image.open('/home/pi/Emiglio/animations/' + self.image_list[self.index][0] + '/' + self.image_list[self.index][1] + '.png').convert("RGB")
                image = np.array(im.getdata())
                next_im = last_draw + float(self.image_list[self.index][2])
                self.index += 1

            # Wait for effects to finish
            effect_wait = effect_thread.done_flag.wait()
            sparkle_wait = sparkle_thread.done_flag.wait()
            
            effect = np.copy(effect_thread.effect_out)
            sparkle = np.copy(sparkle_thread.effect_out)
            
            # Set new_screen array to draw 
            new_screen = np.zeros((256,3))
            
            if self.mask:
                if self.invert:
                    effect[np.nonzero(image)[0]] = np.zeros(np.shape(effect[np.nonzero(image)[0]]))
                    new_screen = np.add(new_screen, effect)
                else:
                    new_screen[np.nonzero(image)[0]] = np.add(new_screen[np.nonzero(image)[0]], effect[np.nonzero(image)[0]])
            else:
                effect[np.nonzero(image)[0]] = np.zeros((len([np.nonzero(image)[0]]),3))
                new_screen = np.add(image, effect)
            
            sleep(max(0, min(next_im - time(), next_effect - time(), next_spark - time())))
        draw_thread.screen = np.zeros((256,3))
        draw_thread.draw_event.set()


class LED_Draw(Thread):
    def __init__(self, strip):
        super(LED_Draw, self).__init__()
        self.screen = np.zeros((256,3))
        self.draw_event = Event()
        self.draw_event.clear()
        self.strip = strip
        self.setDaemon(True)
        self.start()
        
    def run(self,):
        while self.draw_event.wait():
            self.draw_event.clear()
            t_s = time()
            r_2_l = True
            for i in range(0,16):
                for j in range(0,16):
                    # Toggle draw direction because of LED connection
                    if r_2_l:
                        index = (i+1)*16 - 1 - j
                    else:
                        index = i*16 + j
                    r, g, b = self.screen[index]
                    
                    color_out = Color(int(max(min(g, 255), 0)),
                                      int(max(min(r, 255), 0)),
                                      int(max(min(b, 255), 0)))
                    self.strip.setPixelColor(i*16 + j, color_out)
                r_2_l = not r_2_l
            self.strip.show()
            

class LED_Effect(Thread):
    """
    Effect Template Class
    Inherets Thread for multi-threading
    
    args
    frequency - int
    Frequency of LED effect updates
    vars - list
    List of variables, can be different for every effect
    init_val
    Initial effect value
    
    class variables
    
    run_flag - threading.Event()
    Run the effect update once after the run_flag is set
    done_flag - threading.Event()
    Set when the effect is done updating
    
    effect_out - np.array(256,3)
    Output array formatted for face
    effect_in - np.array(16,16)
    """
    def __init__(self, frequency, vars = None, init_val = None):
        super(LED_Effect, self).__init__()
        self.frequency = frequency
        self.run_flag = Event()
        self.done_flag = Event()
        self.run_flag.clear()
        self.done_flag.clear()
        if vars is not None:
            self.vars = vars
        if init_val is not None:
            self.effect_in = init_val
        else:
            self.effect_in = np.array((16,16))
        self.effect_out = np.zeros((256,3))
        # Run in the background
        self.setDaemon(True)
        self.start()
            
    def run(self,):
        while self.run_flag.wait():
            self.done_flag.clear()
            self.run_flag.clear()
            self.effect_out = self.effect_func()
            self.done_flag.set()
    
    def effect_func(self):
        return effect_in
        
        
class Sparkle(LED_Effect):
    def effect_func(self):
        t_s = time()
        spark_add, mul = self.vars
        self.effect_in = np.add(self.effect_in, spark_add)
        # Calculate sparkle based on first few terms of Delta fourier expansion
        effect_out = mul*(1/(2*pi) + 1/pi*(1 + np.cos(.2*self.effect_in) + np.cos(.2*2*self.effect_in) + np.cos(.2*3*self.effect_in) + 
                                       np.cos(.2*4*self.effect_in)+np.cos(.2*5*self.effect_in)))
        #print('Spark: {}'.format(time() - t_s))
        return np.copy(effect_out)


class Fire(LED_Effect):
    def effect_func(self):
        max_decay, min_decay, mul = self.vars
        # Move pixels up the screen by rolling the array
        self.effect_in = np.roll(self.effect_in, 1, axis=0)
        # Set bottom row
        self.effect_in[0] = np.random.rand((16))*.2+.7
        effect_out = np.zeros((256,3))
        # Iterate through each pixel to change output array
        for i in range(0,16):
            for j in range(0,16):
                # Increase the brightness of each pixel based on brightness of surrounding pixels
                if i != 0:
                    self.effect_in[i,j] -= ((max_decay - min_decay)*np.random.rand(1)+min_decay)
                    self.effect_in[i,j] += sum(self.effect_in[i-1,max(0,j-1):min(16,j+2)])/mul
                    if i != 15:
                        self.effect_in[i,j] += sum(self.effect_in[i+1,max(0,j-1):min(16,j+2)])/mul
                    if j != 0:
                        self.effect_in[i,j] += sum(self.effect_in[max(0,i-1):min(16,i+2),j-1])/mul
                    self.effect_in[i,j] = min(1, self.effect_in[i,j])
                # Decrease color vals based on brightness, change color order for diff. colored flames
                # r - g - b = Natural
                # b - r - g = Cool purple
                if 1 >= self.effect_in[i][j] > 2/3:
                    r = 200
                    g = 200
                    b = min(200, max(0, (self.effect_in[i][j] - 2/3)* 200 * 3))
                elif 2/3 >= self.effect_in[i,j] > 1/3:
                    r = 200
                    g = min(200, max(0, (self.effect_in[i][j] - 1/3)* 200 * 3))
                    b = 0
                elif 1/3 >= self.effect_in[i][j] > 0:
                    r = min(200, max(0, (self.effect_in[i][j])* 200 * 3))
                    g = 0
                    b = 0
                else:
                    r = 0
                    g = 0
                    b = 0
                effect_out[(15-i)*16+j] = [int(r),int(g),int(b)]
        return np.copy(effect_out)


class Rainbow_Wipe(LED_Effect):
    def effect_func(self):
        colors, current, color_index, trans_index, color_tran, next = self.vars
        if trans_index < 6:
            if trans_index == 0:
                next = (color_index != 6) * (color_index+1)
                color_tran = np.subtract(colors[next], colors[color_index])/5
                current = colors[color_index]
            current = np.add(current, color_tran)
        elif trans_index == 6:
            current = colors[next]
        self.effect_out = np.roll(self.effect_out, 16, axis = 0)
        self.effect_out[0:16] = current*np.ones((16,3))
        trans_index = (trans_index!=9)*(trans_index+1)
        if trans_index == 0:
            color_index = (color_index!=6)*(color_index+1)
        self.vars = colors, current, color_index, trans_index, color_tran, next
        return np.copy(self.effect_out)
        """
        self.frequency = frequency
        for i in range(256):
            a = np.ones((256,1)) * 255
            self.effect = np.zeros((256,3))
            self.effect[:,:-1] = a
        self.colors = ((255,0,0),
                  (255,75,0),
                  (255,255,0),
                  (0,255,0),
                  (0,100,255),
                  (50,0,255),
                  (255,0,255))
        self.current = (255,0,0)
        self.color_index = 0
        self.trans_index = 0
        self.color_tran = 0
        self.next = (255, 0, 0)
    
    def iterate_effect(self):
        if self.trans_index < 6:
            if self.trans_index == 0:
                self.next = (self.color_index != 6) * (self.color_index+1)
                self.color_tran = np.subtract(self.colors[self.next], self.colors[self.color_index])/5
                self.current = self.colors[self.color_index]
            self.current = np.add(self.current, self.color_tran)
        elif self.trans_index == 6:
            self.current = self.colors[self.next]
        self.effect = np.roll(self.effect, 16, axis = 0)
        self.effect[0:16] = self.current*np.ones((16,3))
        self.trans_index = (self.trans_index!=9)*(self.trans_index+1)
        if self.trans_index == 0:
            self.color_index = (self.color_index!=6)*(self.color_index+1)
        return np.copy(self.effect)
        """
