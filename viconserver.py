from SocketServer import *
import socket, threading
import json
import math

from collections import deque

import streamreader

SERVER_PORT = 4001
VICON_PORT = 801
VICON_HOST = '192.168.20.99'

class ViconRequestHandler(BaseRequestHandler):

	def handle(self):
		self.request.sendall(json.dumps(self.server.get_most_recent_frame()))

class ViconServer(ThreadingMixIn, TCPServer):

	def __init__(self):
		TCPServer.__init__(self, (socket.gethostname(), SERVER_PORT), ViconRequestHandler)

		self.vicon_thread = threading.Thread(target=self.read_vicon_stream)
		self.stop_vicon = False
		self.frames = deque(maxlen=10)

		if not streamreader.connect(VICON_HOST):
			raise Exception("Couldn't connect to vicon system at : {}:{}".format(VICON_HOST, VICON_PORT))

	def read_vicon_stream(self):
		while not self.stop_vicon:
			curr_frame = streamreader.get_frame()
			new_frame = dict()
			if len(self.frames) != 0:
				for car, values in curr_frame.iteritems():
					v = 0
					if car in self.frames[-1]:
						v = math.sqrt(abs(values[0] - self.frames[-1][car][0])**2
							+ abs(values[1] - self.frames[-1][car][1])**2)
					new_frame[car] = (values[0], values[1], values[2], v, values[3])
			else:
				for car, values in curr_frame.iteritems():
					new_frame[car] = (values[0], values[1], values[2], 0, values[3])
			self.frames.append(new_frame)

	def get_most_recent_frame():
		return self.frames[-1]

	def start(self):
		t = threading.Thread(target=self.serve_forever)
		t.daemon = True
		t.start()
		self.vicon_thread.start()
		return t

	def stop(self):
		self.stop_vicon = True
		self.shutdown()
		self.server_close()
		return True

def main():
	test =  ViconServer()

if __name__ == '__main__':
	main()