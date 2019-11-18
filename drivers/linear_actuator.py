import asyncio
import logging

# actuator travel distance in our project is ~33.5cm
# This equates to 1680 steps, which is roughly 20mm/step

class LinearActuator:
  def __init__(self, stepper, lsw0=None, lsw1=None, length=0, position=0):
    self.logger = logging.getLogger(__name__)
    self.stepper = stepper
    self.sw0 = lsw0
    self.sw1 = lsw1
    self.length = length
    self.position = position
    
  #TODO: Create a calibration method to be used if limit switches are present

  def is_running(self):
    return self.stepper.running

  async def step_by(self, steps):
    if self.is_running():
      self.logger.warn("Recieved request to run while already running")
    if self.length and not (self.length > steps > 0):
      self.logger.warn("Distance is outside range of stepper movement")
    
    steps = await self.stepper.step(steps)
    self.position += steps
    self.logger.debug("Actuator moved {} steps from {} to {}".format(steps, self.position-steps, self.position))
    return self.position
  
  async def step_to(self, position):
    distance = position - self.position
    return await self.step_by(distance)


# if __name__ == '__main__':
#   from stepper import Stepper
#   import time
#   stepper = Stepper(20, 21, sl_time=0.00009, sw_time=0, invert_direction=True)
#   linear_actuator = LinearActuator(stepper)
#   logging.basicConfig(level=logging.DEBUG)
#   try:
#     start = time.time()
#     asyncio.run(linear_actuator.step_to(1680))
#     asyncio.run(linear_actuator.step_to(0))
#     difference = time.time() - start
#     logging.info("Reached end and back in {} seconds".format(difference))

#     # for i in range(168,1681,168):
#     #   asyncio.run(linear_actuator.step_to(i))
#     #   asyncio.run(linear_actuator.step_to(0))
#   except KeyboardInterrupt:
#     pass


