import threading
import math
import time

import utils
import streamreader

class ViconClient(object):

	def __init__(self, destination):
		self._frames = destination # reference to add frames to
		self._stop_stream = False
		self._stream_thread = threading.Thread(target=self._receive_frames)

		print "Connecting to Vicon..."
		if not streamreader.connect(utils.VICON_HOST):
			raise Exception("Couldn't connect to vicon system at : {}:{}".format(utils.VICON_HOST, utils.VICON_PORT))

	def _receive_frames(self):
		"""
		Get frames from Vicon, compute velocities, and at the frames to the destination queue
		"""

		while not self._stop_stream:
			prev_frame = dict()
			if len(self._frames) > 0:
				prev_frame = self._frames[-1]

			curr_frame = streamreader.get_frame()
			new_frame = dict()

			for car, values in curr_frame.iteritems():
				v = 0
				if car in prev_frame:
					v = math.sqrt(abs(values[0] - prev_frame[car][0])**2
						+ abs(values[1] - prev_frame[car][1])**2)
				new_frame[car] = (values[0], values[1], values[2], v, values[3])

			self._frames.append(new_frame)
			time.sleep(utils.VICON_SERVER_SLEEP) # allows other threads a chance to access frames

	def start(self):
		self._stream_thread.start()
	
	def close(self):
		self._stop_stream = True
		self._stream_thread.join()

# Testing

from collections import deque

def main():
	d = deque(maxlen=3)
	c = ViconClient(d)
	c.start()
	try:
		while True:
			inp = raw_input('Kill? ')
			if inp == 'y':
				break
			print d[-1]
	except KeyboardInterrupt:
		pass
	c.close()

if __name__ == '__main__':
	main()
