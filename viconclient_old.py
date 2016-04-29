import socket
import json
import threading
import struct

import utils

class ViconClient(object):

	def __init__(self, host, port, destination):
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._frames = destination # reference to add frames to
		self._stop_stream = False
		self._stream_thread = threading.Thread(target=self._receive_frames)
		try:
			self._socket.connect((host, port))
		except socket.error:
			print "Failed to connect to Vicon server:", (host,port)

	def _receive_frames(self):
		while not self._stop_stream:
			try:
				self._socket.sendall("blah")
				buf = utils.recvall(self._socket, 4)
				length, = struct.unpack('!I', buf)
				frame = json.loads(utils.recvall(self._socket, length))
				self._frames.append(frame)

				print self._frames[-1]
			except socket.error:
				print 'connection to server died'
				break

	def get_frame(self):
		if len(self._frames) > 0:
			return self._frames[-1]
		return None

	def start(self):
		self._stream_thread.start()
	
	def close(self):
		self._stop_stream = True
		self._stream_thread.join()
		self._socket.close()

# Testing

from collections import deque

def main():
	d = deque(maxlen=3)
	c = ViconClient('IP_HERE', utils.SERVER_PORT, d)
	c.start()
	try:
		while True:
			inp = raw_input('Kill? ')
			if inp == 'y':
				break
			print len(d)
	except KeyboardInterrupt:
		pass
	c.close()

if __name__ == '__main__':
	main()
