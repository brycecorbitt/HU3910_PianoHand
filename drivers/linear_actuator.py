from serial_control import PacketFactory
import threading
import logging


class LinearActuator:
  def __init__(self, serial_controller, st_time=1000, sw_time=800, starting_position=0):
    self.serial_controller = serial_controller
    self.step_time = st_time
    self.switch_time = sw_time
    self.position = starting_position
    self.run_lock = threading.Lock()
    self.step_request_lock = threading.Lock()
    self.running = False
  
  def is_running(self):
    self.run_lock.acquire()
    val = self.running
    self.run_lock.release()
    return val
  
  def set_running(self, val):
    self.run_lock.acquire()
    self.running = val
    self.run_lock.release()
  
  def calibrate(self):
    message = PacketFactory.calibration_request()
    return self.serial_controller.send_request(message)

  def set_step_delay(self, st_time=None):
    if(st_time):
      self.step_time = st_time
    message = PacketFactory.set_step_delay(self.step_time)
    return self.serial_controller.send_request(message)

  def get_step_delay(self):
    message = PacketFactory.get_step_delay()
    return self.serial_controller.send_request(message)
  
  def zero_motor(self):
    message = PacketFactory.zero_motor()
    return self.serial_controller.send_request(message)

  def set_switch_time(self, sw_time=None):
    if sw_time:
      self.switch_time = sw_time
    message = PacketFactory.set_step_delay(self.sw_time)
    self.serial_controller.send_request(message)
  
  def set_position(self, position):
    self.position = position
    message = PacketFactory.set_position(self.position)
    self.serial_controller.send_request(message)

  def step(self, target_pos=0):
    self.step_request_lock.acquire()
    if self.is_running():
      raise StepperExecutionException("Stepper is already running")
    self.set_running(True)
    message = PacketFactory.step_request(target_pos)
    response = self.serial_controller.send_request(message)
    if response.status == 10:
      self.set_running(True)
      raise StepperExecutionException("Stepper is already running")
    if response.status == message.status:
      self.set_running(False)
    self.position = response.data
    self.step_request_lock.release()
    return response

  def force_stop(self):
    message = PacketFactory.force_stop()
    response = self.serial_controller.send_request(message)
    if(response.data):
      self.set_running(False)
    self.step_request_lock.acquire()
    self.step_request_lock.release()
    return response

  def get_limit_switch(self, index):
    message = PacketFactory.get_limit_switch(index)
    response = self.serial_controller.send_request(message)
    return response

  def get_near_limit_switch(self):
    return self.get_limit_switch(0)
  
  def get_far_limit_switch(self):
    return self.get_limit_switch(1)


class StepperExecutionException(Exception):
  pass


if __name__ == '__main__':
  POSITION_RECORDINGS = [0, 113, 234, 353, 470, 585, 705, 825, 935, 1055, 1175, 1290]

  from serial_control import SerialController
  import time
  import threading
  sc = SerialController('/dev/ttyACM0')
  s = LinearActuator(sc)
  time.sleep(4)
  # print(s.get_near_limit_switch())
  # print(s.get_far_limit_switch())

  # print(s.step(835))
  s.set_step_delay(1000)
  # val = s.calibrate().data
  # print(val)
  # while(True):
  #   print(s.step(0))
  #   print(s.step(1502))
  #   # print(val)
  #   s.step(0)
  # while(True):
  #   s.step(113)
  #   time.sleep(.2)
  #   s.step(0)
  #   time.sleep(1)

  while True:
      data = int(input())
      print(s.step(data))
      # for x in POSITION_RECORDINGS:
      #   print(s.step(x))
      #   time.sleep(.2)
      # print(s.step(0))
      # time.sleep(2)
    
