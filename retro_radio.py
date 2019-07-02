import os
import glob
import RPi.GPIO as GPIO
import subprocess
from time import sleep
from random import *

#setup IO
GPIO.setmode(GPIO.BCM)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)#static
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)#song
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)#power
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)#switch26
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)#switch13
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)#switch6
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)#switch5
GPIO.setup(12, GPIO.OUT, initial=GPIO.LOW) #BlueTooth
GPIO.setup(24, GPIO.OUT, initial=GPIO.LOW) #BlueTooth
GPIO.setup(25, GPIO.OUT, initial=GPIO.LOW) #BlueTooth
GPIO.setup(23, GPIO.OUT, initial=GPIO.LOW) #AMP
GPIO.setup(18, GPIO.OUT, initial=GPIO.LOW) #Lights

#get list of songs
fileName30s = glob.glob('/home/music/1930s/*.mp3')
fileName40s = glob.glob('/home/music/1940s/*.mp3')
fileNameXmas = glob.glob('/home/music/xmas/*.mp3')
fileNameWow = glob.glob('/home/music/wow/*.mp3')

toggle_song = GPIO.input(27)
toggle_static = GPIO.input(22)
switch_26 = GPIO.input(26)
switch_13 = GPIO.input(13)
switch_6 = GPIO.input(6)
switch_5 = GPIO.input(5)
count_26 = 0
count_13 = 0
count_6 = 0
count_5 = 0
last_position = 0

RadioPlayer = None
StaticPlayer = None
stop_music = False
start_music = False
stop_static = False
start_static = False


def BlueToothOn(x):
    if(x == False):
        GPIO.output(12, GPIO.LOW)#BlueTooth
        GPIO.output(24, GPIO.LOW)#BlueTooth
        GPIO.output(25, GPIO.LOW)#BlueTooth
    else:
        GPIO.output(12, GPIO.HIGH)#BlueTooth
        GPIO.output(24, GPIO.HIGH)#BlueTooth
        GPIO.output(25, GPIO.HIGH)#BlueTooth


def DebounceSwitch(switch_26, switch_13, switch_6, switch_5, count_26, count_13, count_6, count_5):
    if(switch_26 != GPIO.input(26)):
        count_26 = 0
        switch_26 = GPIO.input(26)
    else :
        count_26 += 1

    if(switch_13 != GPIO.input(13)):
        count_13 = 0
        switch_13 = GPIO.input(13)
    else :
        count_13 += 1

    if(switch_6 != GPIO.input(6)):
        count_6 = 0
        switch_6 = GPIO.input(6)
    else :
        count_6 += 1

    if(switch_5 != GPIO.input(5)):
        count_5 = 0
        switch_5 = GPIO.input(5)
    else :
        count_5 += 1

    return switch_26, switch_13, switch_6, switch_5, count_26, count_13, count_6, count_5


def GetPosition(count_26, count_13, count_6, count_5):
    dCount = 3
    if (GPIO.input(26) == 1 and count_26 > dCount): #position 1 (BlueTooth)
        return 1
    elif (GPIO.input(13) == 0 and count_13 > dCount): #position 2 (1930s)
        return 2
    elif ((GPIO.input(5) == 1 and count_5 > dCount) and
        (GPIO.input(6) == 1 and count_6 > dCount) and
        (GPIO.input(13) == 1 and count_13 > dCount)):#position 3  (1940s)
        return 3
    elif (GPIO.input(6) == 0 and count_6 > dCount): #position 4 (christmas)
        return 4
    elif (GPIO.input(5) == 0 and count_5 > dCount): #position 5 (war of worlds)
        return 5
    else:
        return 0
        

while True:

    #power switch OFF
    if(GPIO.input(16) == 0):
        #stop all music and static
        stop_music = True

        #turn off amp, lights, and bluetooth
        GPIO.output(18, GPIO.LOW)#lights
        GPIO.output(23, GPIO.LOW)#amp
        BlueToothOn(False)
    
    #power Switch ON
    else:
        GPIO.output(18, GPIO.HIGH)#lights
        GPIO.output(23, GPIO.HIGH)#amp

        switch_26, switch_13, switch_6, switch_5, count_26, count_13, count_6, count_5 = DebounceSwitch(switch_26, switch_13, switch_6, switch_5, count_26, count_13, count_6, count_5)

        switch_position = GetPosition(count_26, count_13, count_6, count_5)

        #if switch has changed, stop the music
        if(last_position != switch_position):
            stop_music = True
            last_position = switch_position
            print("Current Switch Position =" + str(last_position))
        
        #Blue Tooth Mode
        if(switch_position == 1):#position 1
            BlueToothOn(True)
            stop_music = True
            stop_static = True
        
        #Music Mode
        else:
            BlueToothOn(False)

            if(toggle_song != GPIO.input(27)):
                toggle_song = GPIO.input(27)

                if(toggle_song == True):
                    start_music = True
                else:
                    stop_music = True

            if(toggle_static != GPIO.input(22)):
                toggle_static = GPIO.input(22)

                if(toggle_static == True):
                    stop_static = True
                else:
                    start_static = True
                    

            if (toggle_song == True and (RadioPlayer == None or RadioPlayer.poll() == 0 )):
                start_music = True

            if (toggle_static == False and ( StaticPlayer == None or StaticPlayer.poll() == 0)):
                start_static = True

    if(start_music):
        start_music = False
        print("Play Music")
        if (switch_position == 2): #position 2 (1930s)
            RadioPlayer = subprocess.Popen(['omxplayer', '-olocal',  fileName30s[randint(0, len(fileName30s) - 1)]], stdin=subprocess.PIPE)
        
        elif (switch_position == 3):#position 3 (1940s)
            RadioPlayer = subprocess.Popen(['omxplayer', '-olocal',  fileName40s[randint(0, len(fileName40s) - 1)]], stdin=subprocess.PIPE)

        elif (switch_position == 4): #position 4 (christmas)
           RadioPlayer = subprocess.Popen(['omxplayer', '-olocal',  fileNameXmas[randint(0, len(fileNameXmas) - 1)]], stdin=subprocess.PIPE)
        
        elif (switch_position == 5): #position 5 (war of worlds)
            RadioPlayer = subprocess.Popen(['omxplayer', '-olocal',  fileNameWow[randint(0, len(fileNameWow) - 1)]], stdin=subprocess.PIPE)

    if(stop_music):
        stop_music = False
        if((RadioPlayer != None and RadioPlayer.poll() != 0 )):
            RadioPlayer.stdin.write("q")
            RadioPlayer = None
            print("Stop Music")


    if(start_static):
        start_static = False
        print("Play Static")
        StaticPlayer = subprocess.Popen(['omxplayer', '-olocal', '-loop',  '/home/music/static/static.mp3'], stdin=subprocess.PIPE)    
    
    if(stop_static):
        stop_static = False
        if((StaticPlayer != None and StaticPlayer.poll() != 0 )):
            StaticPlayer.stdin.write("q")
            StaticPlayer = None
            print("Stop Static")

    sleep(0.25) #cheap debouncer
