from serial_control import PacketFactory
import threading
import logging


class Stepper:
  def __init__(self, serial_controller, st_time=1000, sw_time=800, starting_position=0):
    self.serial_controller = serial_controller
    self.step_time = st_time
    self.switch_time = sw_time
    self.position = starting_position
    self.run_lock = threading.Lock()
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

  def set_step_delay(self, st_time=None):
    if(st_time):
      self.step_time = st_time
    message = PacketFactory.set_step_delay(self.step_time)
    self.serial_controller.send_request(message)

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
    return response

  def force_stop(self):
    message = PacketFactory.force_stop()
    response = self.serial_controller.send_request(message)
    if(response.data):
      self.set_running(False)
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
  from serial_control import SerialController
  import time
  import threading
  sc = SerialController('/dev/ttyACM0')
  s = Stepper(sc)
  time.sleep(2)
  print(s.get_near_limit_switch())
  print(s.get_far_limit_switch())
  t = threading.Thread(target=s.step, args=[0])
  t.start()
  t.join()