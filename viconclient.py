import socket
import json
import threading
import struct
from collections import deque

SERVER_PORT = 4001

class ViconClient(object):

	def __init__(self, host, port):
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._frames = deque(maxlen=3)
		self._stop_stream = False
		self._stream_thread = threading.Thread(target=self._receive_frames)
		self._socket.connect((host, port))

	def _receive_frames(self):
		while not self._stop_stream:
			self._socket.send("hello")
			buf = self._recvall(4)
			length, = struct.unpack('!I', buf)
			frame = json.loads(self._recvall(length))
			self._frames.append(frame)
	
	def _recvall(self, count):
		buf = b''
		while count:
			try:
				newbuf = self._socket.recv(count)
			except:
				return None
			if not newbuf:
				return None
			buf += newbuf
			count -= len(newbuf)
		return buf

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

def main():
	s = ViconClient('127.0.1.1', SERVER_PORT)
	s.start()
	while True:
		inp = raw_input('Get frame? ')
		if inp == 'n':
			break
		print s.get_frame()

	s.close()

if __name__ == '__main__':
	main()
