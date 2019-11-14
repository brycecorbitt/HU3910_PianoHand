import RPi.GPIO as GPIO
import asyncio

#use the broadcom layout for the gpio
GPIO.setmode(GPIO.BCM)


class Stepper:
  def __init__(self, d_pin, s_pin, sl_time=0.001, sw_time=0.00001):
    self.direction_pin = d_pin
    self.step_pin = s_pin
    self.sleep_time = sl_time
    self.switch_time = sw_time
    self.direction = GPIO.LOW
    self.running = False
    GPIO.setup(self.direction_pin, GPIO.OUT)
    GPIO.setup(self.step_pin, GPIO.OUT)
    GPIO.output(self.direction_pin, GPIO.LOW)
    GPIO.output(self.step_pin, GPIO.LOW)

  def __del__(self):
    GPIO.cleanup()
  
  async def calibrate(self):
    for i in range(0,100,10):
      await self.step(-1*i)
      await self.step(i)


  def set_sleep_time(self, sl_time):
    self.sleep_time = sl_time

  def set_switch_time(self, sw_time):
    self.switch_time = sw_time
  
  def set_direction(self, direction):
    self.direction = GPIO.HIGH if direction else GPIO.LOW
    GPIO.output(self.direction_pin, self.direction)

  async def step(self, steps=1):
    if self.running:
      raise StepperExecutionException("Stepper motor already running.")

    self.running = True
    direction = GPIO.HIGH if steps < 0 else GPIO.LOW
    if self.direction != direction:
      self.set_direction(direction)
    
    for i in range(abs(steps)):
      if not self.running:
        return i
      GPIO.output(self.step_pin, GPIO.HIGH)
      await asyncio.sleep(self.switch_time)
      GPIO.output(self.step_pin, GPIO.LOW)
      await asyncio.sleep(self.sleep_time)

    self.running = False
    return steps
  
  def force_stop(self):
    self.running = False

class StepperExecutionException(Exception):
  pass


# stepper = Stepper(20, 21)

# loop = asyncio.get_event_loop()
# asyncio.run(stepper.calibrate())
# t1 = loop.create_task(stepper.step(2000))
# async def test():
#   await asyncio.sleep(2)
#   print("Testing Force Stop")
#   stepper.force_stop()
# async def test_2():
#   try:
#     await stepper.step(100)
#   except StepperExecutionException:
#     print("Successfully caught expected StepperExecutionException")
#   await asyncio.sleep(2)
#   await stepper.step(-5000)
#   await stepper.step(5000)
# t2 = loop.create_task(test())
# t3 = loop.create_task(test_2())
# loop.run_until_complete(asyncio.gather(t1, t2, t3))
# loop.close()
# while True:
#   asyncio.run(stepper.step(1000))
#   print("test")
#   asyncio.run(stepper.step(-1000))