import serial
import threading
import logging
import time

class Packet:
		ID_SIZE = 1
		STATUS_SIZE = 1
		DATA_SIZE = 2
		PACKET_SIZE = ID_SIZE + STATUS_SIZE + DATA_SIZE
		PACKET_TYPES = {0: "Calibrate", 1: "Step Request", 2: "Set Position",
			3: "Get Position", 4: "Set Switch Delay", 5: "Get Switch Delay", 6: "Set Step Delay",
			7: "Get Step Delay", 8: "Force Stop", 9: "Get Limit Switch", 10: "Step Error", 11: "Stopped Request"}

		def __init__(self, id, status, data):
			if id > 2**(Packet.ID_SIZE*8) or id < 0:
				raise ValueError("Packet id out of range (got {})".format(id))
			if status > 2**(Packet.STATUS_SIZE*8) -1 or status < 0:
				raise ValueError("Packet status out of range (got {})".format(status))
			if data > 2**(Packet.DATA_SIZE*8 -1) -1 or data < -1 * (2**(Packet.DATA_SIZE*8) -1):
				raise ValueError("Packet data out of range (got {})".format(data))
			self.id = id
			self.status = status
			if self.status not in Packet.PACKET_TYPES:
				self.type = "Unknown"
			else:
				self.type = Packet.PACKET_TYPES[self.status]
			self.data = data
			
		@classmethod
		def from_bytes(cls, bytes):
			if len(bytes) !=  Packet.PACKET_SIZE:
				raise ValueError("Packets must be {} bytes in length".format(Packet.PACKET_SIZE))
			id = int(bytes[0])
			status = int(bytes[1])
			data = int.from_bytes(bytes[2:], byteorder='big', signed=True)
			return cls(id, status, data)
		
		def to_bytes(self):
			id = self.id.to_bytes(Packet.ID_SIZE, byteorder='big')
			status = self.status.to_bytes(Packet.STATUS_SIZE, byteorder='big')
			data = self.data.to_bytes(Packet.DATA_SIZE, byteorder='big', signed=True)
			return id + status + data
		
		def __repr__(self):
			return ("Packet(id={}, status={}, type=\"{}\", data={})".format(self.id, self.status, self.type, self.data))


class PacketFactory:
	id = 0
	@staticmethod
	def get_next_id():
		id = PacketFactory.id
		PacketFactory.id += 1
		if(PacketFactory.id > 2**(Packet.ID_SIZE*8) -1):
			PacketFactory.id = 0
		return id

	@staticmethod
	def calibration_request():
			return Packet(PacketFactory.get_next_id(), 0, 0)
	@staticmethod		
	def step_request(target_position):
		 	return Packet(PacketFactory.get_next_id(), 1, target_position)
	@staticmethod
	def set_position(position):
			return Packet(PacketFactory.get_next_id(), 2, position)
	@staticmethod
	def get_position():
			return Packet(PacketFactory.get_next_id(), 3, 0)
	@staticmethod
	def set_switch_delay(delay):
			return Packet(PacketFactory.get_next_id(), 4, delay)
	@staticmethod
	def get_switch_delay():
			return Packet(PacketFactory.get_next_id(), 5, 0)
	@staticmethod
	def set_step_delay(delay):
			return Packet(PacketFactory.get_next_id(), 6, delay)
	@staticmethod
	def get_step_delay():
			return Packet(PacketFactory.get_next_id(), 7, 0)
	@staticmethod
	def force_stop():
			return Packet(PacketFactory.get_next_id(), 8, 0)
	@staticmethod
	def get_limit_switch(number):
			return Packet(PacketFactory.get_next_id(), 9, number)


# '/dev/ttyACM0' is default device for arduino, 9600 is default baud rate
class SerialController:
	QUERY_DELAY = .005
	INIT_DELAY = 2
	def __init__(self, device='/dev/ttyACM0', baud_rate=9600):
		self.logger = logging.getLogger(__name__)
		self.device = device
		self.baud_rate = baud_rate
		self.serial = serial.Serial(self.device, self.baud_rate)
		self.packet_lock = threading.Lock()
		self.packets = {}
		self.process_thread = threading.Thread(target=self.process_serial, daemon=True)
		
		self.process_thread.start()
	
	def process_serial(self):
		time.sleep(SerialController.INIT_DELAY)
		while True:
			incoming_msg = self.serial.read(Packet.PACKET_SIZE)
			packet = Packet.from_bytes(incoming_msg)
			self.logger.info("Recieved data from serial device: {}".format(packet))
			self.packet_lock.acquire()
			self.packets[packet.id] = packet
			self.packet_lock.release()
			time.sleep(.1)
	
	def send_packet(self, packet):
		# It is OK to use this in the main thread, as pyserial is thread safe.
		self.serial.write(packet.to_bytes())
		self.logger.info("Sent data to serial device: {}".format(packet))

	def query_response(self, id):
		packet = None
		while not packet:
			self.packet_lock.acquire()
			if id in self.packets:
				packet = self.packets[id]
				del self.packets[id]
				self.packet_lock.release()
			else:
				self.packet_lock.release()
				time.sleep(SerialController.QUERY_DELAY)
		return packet
	
	def send_request(self, packet):
		self.send_packet(packet)
		return self.query_response(packet.id)


    

# if __name__ == '__main__':
# 	logging.basicConfig(level=logging.INFO)
# 	sc = SerialController()
# 	# send/recieve messages
# 	time.sleep(SerialController.INIT_DELAY)
# 	logging.info("Test Getting Values")
# 	asyncio.run(sc.send_request(PacketFactory.set_position(1680)))
# 	asyncio.run(sc.send_request(PacketFactory.get_position()))
# 	asyncio.run(sc.send_request(PacketFactory.set_switch_delay(500)))
# 	asyncio.run(sc.send_request(PacketFactory.get_switch_delay()))
# 	asyncio.run(sc.send_request(PacketFactory.set_step_delay(800)))
# 	asyncio.run(sc.send_request(PacketFactory.get_step_delay()))

