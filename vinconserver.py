from SocketSever import *
import socket, threading

import streamreader

SERVER_PORT = 1001
VICON_PORT = 801
VICON_HOST = '192.168.20.99'

class ViconRequestHandler(BaseRequestHandler):

	def handle(self):
		pass		

class ViconServer(ThreadingMixIn, TCPServer):

	def __init__(self):
		super(TCPServer, self).__init__((socket.gethostname(), PORT), ViconRequestHandler)

		self.vicon_thread = None

		if !streamreader.connect(VICON_HOST):
			raise Exception("Couldn't connect to vicon system at : {}:{}".format(VICON_HOST, VICON_PORT))

		# set up frame grabbing

	def start(self):
		t = threading.Thread(target=self.serve_forever)
		t.daemon = True
		t.start()
		# TODO start getting frames from vicon
		return t

	def stop(self):
		# TODO kill vicon
		self.shutdown()
		self.server_close()
