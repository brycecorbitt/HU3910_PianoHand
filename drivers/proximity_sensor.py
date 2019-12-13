import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

class ADC:
  available_channels = list(range(0,8))
  allocated_channels = []
  # create the spi bus
  spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
  
  # create the cs (chip select)
  cs = digitalio.DigitalInOut(board.D5)
  
  # create the mcp object
  mcp = MCP.MCP3008(spi, cs)

  @staticmethod 
  def add_channel(number):
    if number in ADC.allocated_channels:
      print("Warning: This channel has already been allocated")
      return AnalogIn(ADC.mcp, number)
    elif number not in ADC.available_channels:
      print("Error: Channel number outside available range")
      return
    ADC.available_channels.remove(number)
    ADC.allocated_channels.append(number)
    return AnalogIn(ADC.mcp, number)

# Code to test ADC by printing out channel 0 voltage
import time
channel = ADC.add_channel(0)
while True:
    print(channel.voltage, end="\r", flush=True)
    time.sleep(.2)