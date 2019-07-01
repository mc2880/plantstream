import time
from neopixel import NeoPixel
import machine
import network
import socket
import urequests
import gc
import math
gc.collect()
print("The garbage man can")

NETWORKSSID = 'ssid'
NETWORKPASSWORD = 'password'
API_URL = 'http://your.api'


def do_connect():
    
    
    
    sta_if = network.WLAN(network.STA_IF)
    
    try:
      sta_if.disconnect()
    except:
      pass
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(NETWORKSSID, NETWORKPASSWORD)
        while not sta_if.isconnected():

            pass
    print('network config:', sta_if.ifconfig())

do_connect()

def valmap(value, istart, istop, ostart, ostop):
  return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))

def makesacledpixels(input_text):
  pixel_vals = []
  for i in range(0, len(input_text)):
    pixel_vals.append(int(input_text[i]))

  howmanypx = int(len(pixel_vals) / 3)

  pixels = []

  for i in range(0, howmanypx,3):
    r = int(valmap(pixel_vals[i], 10,130,0,255))
    g = int(valmap(pixel_vals[i+1], 10,130,0,255))
    b = int(valmap(pixel_vals[i+2], 10,130,0,255))
    pixels.append((r,g,b))

  return(pixels)

def MakeRainbow(incr, freq1, freq2, freq3, phase1, phase2, phase3, center, width):
  #Highly stolen from https://krazydad.com/tutorials/makecolors.php
  red = math.sin(freq1 * incr + phase1) * width + center
  green = math.sin(freq2 * incr + phase2) * width + center
  blue = math.sin(freq3 * incr + phase3) * width + center
  
  pixelcolour = (int(red),int(green),int(blue))
  
  return pixelcolour

def brightness(pixel):
  output_pixel = (int(pixel[0] * (BRIGHTNESS/100)),int(pixel[1] * (BRIGHTNESS/100)),int(pixel[2] * (BRIGHTNESS/100)))
  return(output_pixel)

def minmaxpx(pixel):
  pixelmx = list(pixel)
  pixelmx[pixelmx.index(max(pixelmx))] = 255
  pixelmx[pixelmx.index(min(pixelmx))] = 0

  return(pixelmx)

def displayout(pixelbank,npnum,npcnt):

  i = 0
  timeout = 1
  try:
    timeout = 1 / (len(pixelbank)/npcnt)
  except:
    pass
  while len(pixelbank) > 0:
    npnum.fill((0,0,0))
    npnum.write()
    for j in range(0,npcnt):
      try:

        npnum[j] = brightness(minmaxpx(pixelbank[i]))
        i += 1
      except:
        pass
    npnum.write()
    time.sleep(timeout)
    pixelbank.pop(0)
    i=0

  time.sleep(timeout)
  npnum.fill((0,0,0))
  npnum.write()


def marquee(strip,colour1,colour2):
  if tick_tock % 2 == 0:
    #print("even")
    strip.fill(brightness(colour1))
    for i in range(0, numnp1,2):
      strip[i] = brightness(colour2)
  else:
    #print("odd")
    strip.fill(brightness(colour1))
    for i in range(1, numnp1,2):
      strip[i] = brightness(colour2)
  strip.write()
  

def chase(strip,background,foreground):
  strip.fill(brightness(background))
  for i in range(0,int(numnp1 * (tick_tock/20))):
    strip[i] = brightness(foreground)
  strip.write()
  
  
def rainbow(strip):
    for i in range(0,numnp1):
      strip[i] = MakeRainbow(int(tick_tock+i),5,2,.5,0,0,0,numnp1,numnp1)
      strip.write() 

def singlecolour(strip,colour):
  strip.fill(brightness(colour))
  strip.write()
BRIGHTNESS = 40 # 0 - 100

numnp1 = 19    # number of pixels on the strip
pinnp1 = machine.Pin(14)


np1 = NeoPixel(pinnp1, numnp1)
#np1.timing = True            #ESP32 is different and this makes everything work instead of not work!!!!!!1
np1.fill((0,0,0))
np1.write()

RED = (255,0,0)
WHITE = (150,255,255)
YELLOW = (255,255,0)
GREEN = (0,255,0)
AQUA = (0,255,255)
BLUE = (0,0,255)
PINK = (200,0,255)
PURPLE = (125,0,255)


tick_tock = 0
move_type = 'rainbow'
last_move_update = time.ticks_ms()


while True:
  #print("it work?")

  delta_time = time.ticks_diff(time.ticks_ms(), last_move_update)

  if delta_time >= 15000:
      
    try:
      response2 = urequests.get(API_URL + '/cntower/out')
      movement = str(response2.text, 'utf-8')
      response2.close()
      last_move_update = time.ticks_ms()
      if len(movement) >= 3:
        print(movement)
        move_type = movement.split(";")[0]
        move_value = movement.split(";")[1]
        tick_tock = 0
        
        response = urequests.get(API_URL + '/camera/abs?user=admin&cm=25') #move the camera to see the tower
        response.close()
        

    except:
     response2.close()
     print("couldn't get anyhting")
      

  if move_type == 'marquee':
    marquee(np1,WHITE,RED)
  elif move_type == 'chase':
    chase(np1,WHITE,RED)
  elif move_type == 'rainbow':
    rainbow(np1)
  else:
    news = False
  
  time.sleep(.5)
  tick_tock += 1
  #print(tick_tock)
  print(delta_time)
  print(move_type)
  if tick_tock >= 20:
    tick_tock = 0
  



