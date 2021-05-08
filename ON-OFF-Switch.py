
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)


toggle = GPIO.input(16)

while True:

    if(toggle != GPIO.input(16)):
        toggle = GPIO.input(16)
        if(toggle == True):
            print("HIGH")
        else:
            print("LOW")
