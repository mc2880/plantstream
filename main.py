
from machine import UART, Pin, Timer, PWM
import time
import network
import socket
import urequests

def do_connect():
    
    
    
    sta_if = network.WLAN(network.STA_IF)
    
    try:
      sta_if.disconnect()
    except:
      pass
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('SSDI', 'PASSWORD')
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())


do_connect()


step_dir = Pin(14, Pin.OPEN_DRAIN)
step_step = Pin(16, Pin.OUT)


relay1 = Pin(4, Pin.OUT)
relay2 = Pin(5, Pin.OUT)

stop1 = Pin(13, Pin.IN, Pin.PULL_UP) # Left Stop
stop2 = Pin(12, Pin.IN, Pin.PULL_UP) # Right Stop


relay1.value(0) # Stepper
relay2.value(0) # Water

sleep_time = 1000



position = 0        # track the position of the camera
left_position = 0   # Find the length of the camera track


def moveleft(steps,delay):
  global step_dir, step_dir, position
  
  step_dir.value(0)
  for i in range(steps):
    if stop1.value() == 0:
      step_step.value(1)
      time.sleep_us(delay)
      step_step.value(0)
      time.sleep_us(delay)
      position += 1
    elif stop1.value() ==1:
      print("Found left limit at:" + str(position))
      break
    

def moveright(steps,delay):
  global step_dir, step_dir, position
  
  step_dir.value(1)
  for i in range(steps):
    if stop2.value() == 0:
      step_step.value(1)
      time.sleep_us(delay)
      step_step.value(0)
      time.sleep_us(delay)
      position += -1
    elif stop2.value() == 1:
      print("Found right limit at :" + str(position))
      break

def findright(steps,delay):
  global step_dir, step_dir, position

  step_dir.value(1)
  for i in range(steps):
    if stop2.value() == 0:
      step_step.value(1)
      time.sleep_us(delay)
      step_step.value(0)
      time.sleep_us(delay)
      position += -1
    else:
      return_steps = position
      position = 0
      return return_steps
      
def findleft(steps,delay):
  global step_dir, step_dir, position, left_position

  step_dir.value(0)
  for i in range(steps):
    if stop1.value() == 0:
      step_step.value(1)
      time.sleep_us(delay)
      step_step.value(0)
      time.sleep_us(delay)
      position += 1
    else:
      left_position = position
      return left_position
      

relay1.value(1)
time.sleep(.1)
print(findright(100000,10))
print(position)
print(findleft(200000,10))
print("left position: " + str(left_position))
moveright(left_position/2,10)
relay1.value(0)


last_movement = 0

while True:
  # Check for new movements
  try:
    response2 = urequests.get('YOUR API ENDPOINT HERE')
    movement = str(response2.text, 'utf-8')
    print("Response: " + str(movement))
    movement = int(movement)
  except:
    print("Not a valid response from the server")
    
  if int(movement) > 0:
    
    last_movement = time.ticks_ms()
    relay1.value(1)
    moveleft(int(movement),30)
    
  elif int(movement) < 0:
    
    last_movement = time.ticks_ms()
    relay1.value(1)
    moveright((int(movement) * -1),30)
  
  relay1.value(0)       #  turn off the stepper driver
  
  print(last_movement)
  print(time.ticks_ms())
  delta = time.ticks_diff(time.ticks_ms(), last_movement)
  print(delta)
  
  if delta >= 30000:

    to_centre = (left_position/2) - position

    if to_centre > 0:
      relay1.value(1)
      moveleft(to_centre,100)
      relay1.value(0)

    if to_centre < 0:
      relay1.value(1)
      moveright(to_centre,100)
      relay1.value(0)   
  
  time.sleep(1)


  





