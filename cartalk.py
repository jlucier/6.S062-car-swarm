import socket
from SocketServer import *
from Queue import Queue, Empty
import threading

import utils

class Message(object):
    ROW = 'ROW'
    STAY = 'STAY'
    GO = 'GO'

    def __init__(self, m_type, my_name, other_name, location, frame_num, priority_val=0):
        self.type = m_type
        self.my_name = my_name # only used for outgoing messages, None otherwise
        self.other_name = other_name
        frame_num = frame_num
        self.location = location
        self.priority_val = priority_val

    def make_message(self):
        return json.dumps({'name':self.my_name, 'type':self.type, 'location':self.location,
            'frame_num':self.frame_num,  'priority_val':self.priority_val})

class CarClient(object):
	"""
	Class for sending messages to other cars
	"""

    def __init__(self, car_ips):
        self._queue = Queue()
        self._kill = False
        self._car_sockets = dict()
        self._car_ips = car_ips

        for name, ip in car_ips.iteritems():
            self._car_sockets[name] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self._thread = threading.Thread(target=self._send)

    def _send(self):
        while not self._kill:
            try:
                message = self._queue.get(timeout=utils.QUEUE_TIMEOUT)
            except Empty:
                continue

            s = self._car_sockets[message.other_name]
            text = message.make_message()
            s.sendall(struct.pack('!I', len(text)))
            s.sendall(text)

    def send_message(self, message):
        self._queue.put(message)

    def start(self):
        for name, s in self._car_sockets.iteritems():
            s.connect((self.car_ips[name], utils.CAR_PORT))

        self._thread.start()

    def stop(self):
        self._kill = True
        self._thread.join()
        for s in self._car_sockets.values():
            s.close()
        return True

class CarRequestHandler(BaseRequestHandler):

    def handle(self):
        try:
            while not self.server._kill:
                buf = utils.recvall(self.request, 4)
                length, = struct.unpack('!I', buf)
                data = json.loads(utils.recvall(self.request, length))
                # create message so that other_name is the car that sent the message
                message = Message(data['type'], None, data['name'], data['location'], data['frame_num'],
                    priority_val=data['priority_val'])
                self.server._queue.put(message)

        except socket.error:
            pass

class CarServer(ThreadingMixIn, TCPServer):
    """
    Accepts messages from other cars, communicate messages back to main loop
    """
    
    def __init__(self):
        TCPServer.__init__(self, (socket.gethostname(), utils.CAR_PORT), CarRequestHandler)
        self._kill = False
        self._queue = Queue()

    def get_message(self):
        try:
            return self._queue.get() # TODO figure out if we need to block
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

    def send_message(self, message):
        self._client.send_message(message)
        return True

    def get_message(self):
        """
        Gets incoming message if there is one (None otherwise)
        """
        return self._server.get_message()

    def start(self):
        # TODO workout timing so the cars can connect properly
        self._server.start()
        self._client.start()

    def stop(self):
        self._client.stop()
        self._server.stop()
        return True
