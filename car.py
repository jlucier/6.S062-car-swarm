import threading
import time
import math
from collections import deque
from Queue import Queue, Empty

import utils
from viconclient import ViconClient
from cartalk import CarTalker
from driver import Driver, Preset

class Car(object):
    """
    Car class:
        - main module in the system
        - orchestrates collision detection and processing, as well as car-to-car communication
    """

    def __init__(self, path=None):
        f = open(utils.NAME_FILE, 'r')
        car_name = f.read().strip()
        f.close()

        self.name = car_name
        self.frames = deque(maxlen=5) # frame = {'car_name': (x,y,theta,v,t), ...}
        self._kill = False
        self._last_frame_number = 0
        self._collision_worker = threading.Thread(target=self._detect_collisions)
        self._message_worker = threading.Thread(target=self._process_messages)
        self._main_worker = threading.Thread(target=self._process_collisions)
        self._collisions = Queue()

        car_ips = dict()
        ips = utils.get_car_ips()

        for name, ip in ips.iteritems():
            if name != self.name:
                car_ips[name] = ip

        self._vicon_client = ViconClient(self.frames)
        # self._talker = CarTalker(car_ips)
        self._driver = None

        if path:
            self._driver = Driver(path=path)
        else:
            self._driver = Driver()
    
    def _detect_collisions(self):
        """
        Collision detector:
            - detects future collisions between self and other cars
            - creates new Collision objects and sends them to the main queue
        """

        distance_between = lambda p1, p2: math.sqrt(abs(p1[0] - p2[0])**2 + abs(p1[1] - p2[1])**2)
        collide = lambda c1, c2: distance_between(c1, c2) <= utils.MIN_DISTANCE

        while not self._kill:
            if len(self.frames) == 0:
                continue
            curr_frame = self.frames[-1]
            my_vals = curr_frame[self.name]

            if self._last_frame_number >= my_vals[-1]:
                continue

            self._last_frame_number = my_vals[-1]

            # compute vx,vy per car
            car_velocities = dict()
            for car_name, vals in curr_frame.iteritems():
                car_velocities[car_name] = (math.cos(vals[2]) * vals[3], math.sin(vals[2]) * vals[3])

            my_v = car_velocities[self.name]
            # +1 makes loop inclusive
            for dt in xrange(utils.FRAME_STEP, utils.FRAME_LOOKAHEAD + 1, utils.FRAME_STEP):
                my_future_pos = (my_vals[0] + my_v[0] * dt, my_vals[1] + my_v[1] * dt)

                for car_name, vals in curr_frame.iteritems():
                    if car_name == self.name:
                        continue

                    dx = car_velocities[car_name][0] * dt
                    dy = car_velocities[car_name][1] * dt
                    future_pos = (vals[0] + dx, vals[1] + dy)

                    if collide(my_future_pos, future_pos):
                        # TODO build collision
                        print "COLLISION DETECTED:", dt
                        print "my_vals:", my_vals, "      my_v:",my_v
                        print "me:",my_future_pos, "\nother:",future_pos
                        collision = None
                        self._collisions.put(collision)

    def _process_messages(self):
        """
        Message Processor:
            - processes incoming messages from CarTalker
            - creates collision objects and adds them to the queue
        """

        while not self._kill:
            message = self._talker.get_message()
            if message is None:
                continue

            #TODO
            pass

    def _process_collisions(self):
        """
        Collision Processor:
            - main loop
            - processes Collision objects in queue and decides course of action
            - coordinates with other cars
        """

        while not self._kill:
            try:
                collision = self._collisions.get(timeout=utils.QUEUE_TIMEOUT)
            except Empty:
                continue

            #TODO
            pass

    def start(self):
        self._vicon_client.start()
        self._talker.start()
        self._collision_worker.start()
        self._message_worker.start()
        self._main_worker.start()

    def stop(self):
        self._kill = True
        self._vicon_client.stop()
        self._talker.stop()
        self._collision_worker.join()
        self._message_worker.join()
        self._main_worker.join()
        return True

def main():
    car = Car()
    car._vicon_client.start()
    time.sleep(2)
    print "Running..."
    try:
        car._detect_collisions()
    except KeyboardInterrupt:
        pass
    # car.stop()

if __name__ == '__main__':
    main()
