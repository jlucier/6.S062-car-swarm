from SocketServer import *
from Queue import Queue, Empty
import threading

import utils

class CarClient(object):

	def __init__(self, car_ips):
		self._queue = Queue()
		self._kill = False
		self._cars = dict()

		for name, ip in car_ips.iteritems():
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((ip, utils.CAR_PORT))
			self._cars[name] = s

		self._thread = threading.Thread(target=self._send)

	def _send(self):
		while not self._kill:
			try:
				item = self._queue.get(timeout=utils.QUEUE_TIMEOUT)
			except Empty:
				continue

			s = self._cars[item[0]]
			message = json.dumps(item[1])
			s.sendall(struct.pack('!I', len(message)))
			s.sendall(message)

	def send_message(self, item):
		self._queue.put(item)

	def start(self):
		self._thread.start()

	def stop(self):
		self._kill = True
		self._thread.join()
		for s in self._cars.values():
			s.close()
		return True

class CarRequestHandler(BaseRequestHandler):

	def handle(self):
		try:
			while not self.server._kill:
				buf = utils.recvall(self.request, 4)
				length, = struct.unpack('!I', buf)
				message = json.loads(utils.recvall(self.request, length))
				self.server._queue.put(message)

		except socket.error:
			pass

class CarServer(ThreadingMixIn, TCPServer):
	"""
	accepts requests from other cars, communicate messages back to main loop
	"""
	
	def __init__(self):
		TCPServer.__init__(self, (socket.gethostname(), utils.CAR_PORT), CarRequestHandler)
		self._kill = False
		self._queue = Queue()

	def get_message(self):
		try:
			return self._queue.get()
		except Empty:
			return None

	def start(self):
		t = threading.Thread(target=self.serve_forever)
		t.daemon = True
		t.start()
		return t

	def stop(self):
		self._kill = True
		self.shutdown()
		self.server_close()
		return True

class CarTalker(object):
	"""
	manager for the car's interaction (server and client)
	implement as message queues, outgoing and incoming
	"""
	
	def __init__(self, car_ips):
		self._client = CarClient(car_ips)
		self._server = CarServer()

	def send_message(self, target, message):
		self._client.send_message((target, message))
		return True

	def get_message(self):
		"""
		Gets incoming message if there is one (None otherwise)
		"""
		return self._server.get_message()

	def start(self):
		self._client.start()
		self._server.start()

	def stop(self):
		self._client.stop()
		self._server.stop()
		return True
