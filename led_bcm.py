#!/usr/bin/env python
import RPi.GPIO as GPIO
import time

LedPin = 17    # pin17 BCM

def setup_led():
	GPIO.setmode(GPIO.BCM)       # Numbers GPIOs by BCM
	GPIO.setup(LedPin, GPIO.OUT)   # Set LedPin's mode is output
	GPIO.output(LedPin, GPIO.HIGH) # Set LedPin high(+3.3V) to off led

def loop_led():
	while True:
		print '...led on'
		GPIO.output(LedPin, GPIO.LOW)  # led on
		time.sleep(0.5)
		print 'led off...'
		GPIO.output(LedPin, GPIO.HIGH) # led off
		time.sleep(0.5)

def destroy_led():
	GPIO.output(LedPin, GPIO.HIGH)     # led off
	GPIO.cleanup(LedPin)                     # Release resource

def led_on():
        GPIO.output(LedPin, GPIO.LOW)  # led on

def led_off():
        GPIO.output(LedPin, GPIO.HIGH)  # led off

if __name__ == '__main__':     # Program start from here
	setup_led()
	try:
		loop_led()
	except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
		destroy_led()

