from machine import Pin, Timer
led = Pin("LED", Pin.OUT)
timer = Timer()

def blink(timer):
    print("toggle")
    led.toggle()

timer.init(freq=2.5, mode=Timer.PERIODIC, callback=blink)

print("Run")

while True:
    pass