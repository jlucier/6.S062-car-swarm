from SocketServer import *
import socket, threading
import json
import math
import struct
from collections import deque
import time

import streamreader
import utils

# BEGIN TESTING
# import streamreader_mock as streamreader
# import datetime
# END TESTING

class ViconRequestHandler(BaseRequestHandler):

    def handle(self):
        while not self.server._stop_vicon:
            try:
                self.request.recv(4)
                frame = json.dumps(self.server.get_most_recent_frame())
                self.request.sendall(struct.pack('!I', len(frame)))
                self.request.sendall(frame)
            except socket.error:
                print "Connection died:", self.client_address
                break

class ViconServer(ThreadingMixIn, TCPServer):

    def __init__(self):
        TCPServer.__init__(self, (socket.gethostname(), utils.SERVER_PORT), ViconRequestHandler)

        self._vicon_thread = threading.Thread(target=self._read_vicon_stream)
        self._stop_vicon = False
        self._frames = deque(maxlen=10)

        # report ip to server
        if not utils.send_ip(utils.SERVER_NAME, utils.get_ip_address()):
            raise Exception("Couldn't report IP address to API")

        print "Connecting to Vicon..."
        if not streamreader.connect(utils.VICON_HOST):
            raise Exception("Couldn't connect to vicon system at : {}:{}".format(utils.VICON_HOST, utils.VICON_PORT))

    def _read_vicon_stream(self):
        if len(self._frames) == 0:
            curr_frame = streamreader.get_frame()
            new_frame = dict()
            for car, values in curr_frame.iteritems():
                new_frame[car] = (values[0], values[1], values[2], 0, values[3])
            self._frames.append(new_frame)

        while not self._stop_vicon:
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

    def get_most_recent_frame(self):
        if len(self._frames) > 0:
            return self._frames[-1]
        return dict()

    def start(self):
        t = threading.Thread(target=self.serve_forever)
        t.daemon = True
        t.start()
        self._vicon_thread.start()
        return t

    def stop(self):
        self._stop_vicon = True # kills worker as well as request handlers
        self._vicon_thread.join()
        self.shutdown()
        self.server_close()
        return True

def main():
    # For testing purposes
    # test =  ViconServer()
    # test.start()
    # try:
    #   while True:
    #       start = datetime.datetime.now()
    #       frame = test.get_most_recent_frame()
    #       end = datetime.datetime.now()
    #       print "Delay: ", end - start, "\n", frame
    #       inp = raw_input("Server up... kill?")
    #       if inp == 'k':
    #           break
    # except KeyboardInterrupt:
    #   pass
    # test.stop()

    s = ViconServer()
    try:
        s.start()
        raw_input('Server Running...' + str(s.server_address) + '\n')
    except KeyboardInterrupt:
        pass
    print "Server going down... Bye"
    s.stop()

if __name__ == '__main__':
    main()