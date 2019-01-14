#!/usr/bin/env python
import os, errno
import pyaudio
import spl_lib as spl
from scipy.signal import lfilter
import numpy
import lcd1602 as lcd1602
import led_bcm as led

## For web browser handling
#from selenium import webdriver


''' The following is similar to a basic CD quality
   When CHUNK size is 4096 it routinely throws an IOError.
   When it is set to 8192 it doesn't.
   IOError happens due to the small CHUNK size

   What is CHUNK? Let's say CHUNK = 4096
   math.pow(2, 12) => RATE / CHUNK = 100ms = 0.1 sec
'''
CHUNKS = [4096, 9600]       # Use what you need
CHUNK = CHUNKS[1]
FORMAT = pyaudio.paInt16    # 16 bit
CHANNEL = 1    # 1 means mono. If stereo, put 2

'''
Different mics have different rates.
For example, Logitech HD 720p has rate 48000Hz
'''
RATES = [44300, 48000]
RATE = RATES[1]

NUMERATOR, DENOMINATOR = spl.A_weighting(RATE)

SND_SAMPLES = list()
LED_THRESHOLD = 70  # 70 dB threshold

def get_path(base, tail, head=''):
    return os.path.join(base, tail) if head == '' else get_path(head, get_path(base, tail)[1:])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = get_path(BASE_DIR, 'html/main.html', 'file:///')
SINGLE_DECIBEL_FILE_PATH = get_path(BASE_DIR, 'decibel_data/single_decibel.txt')
MAX_DECIBEL_FILE_PATH = get_path(BASE_DIR, 'decibel_data/max_decibel.txt')

'''
Listen to mic
'''
pa = pyaudio.PyAudio()

stream = pa.open(format = FORMAT,
                channels = CHANNEL,
                rate = RATE,
                input = True,
                frames_per_buffer = CHUNK)


def is_meaningful(old, new):
    return abs(old - new) > 3

def update_text(path, content):
    try:
        f = open(path, 'w')
    except IOError as e:
        print(e)
    else:
        f.write(content)
        f.close()

def click(id):
    driver.find_element_by_id(id).click()

def open_html(path):
    driver.get(path)

def update_max_if_new_is_larger_than_max(new, max):
    print("update_max_if_new_is_larger_than_max called")
    if new > max:
        print("max observed")
        #update_text(MAX_DECIBEL_FILE_PATH, 'MAX: {:.2f} dBA'.format(new))
        #click('update_max_decibel')
        return new
    else:
        return max

def addSoundSample(new):
    if (len(SND_SAMPLES) > 300):
        SND_SAMPLES.pop(0)
    SND_SAMPLES.append(new)
    return max(SND_SAMPLES)


def listen(old=0, error_count=0, min_decibel=100, max_decibel=0, prev_led_max=0):
    global lcd
    lcd = lcd1602.LCD()
    print("Listening")
    lcd.clear()
    lcd.message("Listening")
    while True:
        try:
            ## read() returns string. You need to decode it into an array later.
            block = stream.read(CHUNK)
        except IOError as e:
            error_count += 1
            print(" (%d) Error recording: %s" % (error_count, e))
            lcd.clear()
            lcd.message("Error recording")
        else:
            ## Int16 is a numpy data type which is Integer (-32768 to 32767)
            ## If you put Int8 or Int32, the result numbers will be ridiculous
            decoded_block = numpy.fromstring(block, 'Int16')
            ## This is where you apply A-weighted filter
            y = lfilter(NUMERATOR, DENOMINATOR, decoded_block)
            new_decibel = 20*numpy.log10(spl.rms_flat(y))
            if is_meaningful(old, new_decibel):
                old = new_decibel
                print('A-weighted: {:+.2f} dB'.format(new_decibel))
                
                #update_text(SINGLE_DECIBEL_FILE_PATH, '{:.2f} dBA'.format(new_decibel))
                #max_decibel = update_max_if_new_is_larger_than_max(new_decibel, max_decibel)
                max_decibel = addSoundSample(new_decibel)
                lcd.clear()
                lcd.message('Max    New:\n{:+.2f}'.format(max_decibel) + ' {:+.2f} dB'.format(new_decibel))
                if (max_decibel > LED_THRESHOLD):
                    led.led_on()
                else:
                    led.led_off()
                sleep(1) # sleep for 1 second before reading next sample
                #click('update_decibel')


    stream.stop_stream()
    stream.close()
    pa.terminate()

def destroy():
    lcd.destroy()
    led.destroy_led()

if __name__ == '__main__':
    #driver = webdriver.Firefox()
    #open_html(HTML_PATH)
    try:
        led.setup_led()
        listen()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()
    #driver.close()
