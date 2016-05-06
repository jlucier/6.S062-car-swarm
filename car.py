import threading
import time
import math
import random
from collections import deque
from Queue import Queue, Empty

import utils
from viconclient import ViconClient
from cartalk import CarTalker, Message
from driver import Driver, Preset
from collision import Collision, CollisionState

class CarState(object):
    """
    Car's movment state
    """
    IDLE = 0
    DRIVING = 1
    STOPPED = 2

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
        self.frames = deque(maxlen=5) # frame = {'car_name': (x,y,theta,vx,vy,t), ...}
        self._state = CarState.IDLE
        self._kill = False
        self._last_frame_number = 0
        self._collision_worker = threading.Thread(target=self._detect_collisions)
        self._message_worker = threading.Thread(target=self._process_messages)
        self._main_worker = threading.Thread(target=self._process_collisions)
        self._collisions = dict() # {'car_name': collision_object ...}

        car_ips = dict()
        ips = utils.get_car_ips()

        for name, ip in ips.iteritems():
            if name != self.name:
                car_ips[name] = ip

        self._vicon_client = ViconClient(self.frames)
        self._talker = CarTalker(car_ips)
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

        while not self._kill:
            if len(self.frames) == 0:
                continue
            curr_frame = self.frames[-1]
            my_vals = curr_frame[self.name]

            # don't waste time on old frames
            if self._last_frame_number >= my_vals[-1]:
                continue

            self._last_frame_number = my_vals[-1]

            # +1 makes loop inclusive
            for dt in xrange(utils.FRAME_STEP, utils.FRAME_LOOKAHEAD + 1, utils.FRAME_STEP):
                my_future_pos = (my_vals[0] + my_vals[3] * dt, my_vals[1] + my_vals[4] * dt)

                for car_name, vals in curr_frame.iteritems():
                    if car_name == self.name:
                        continue

                    dx = vals[3] * dt
                    dy = vals[4] * dt
                    future_pos = (vals[0] + dx, vals[1] + dy)

                    if not utils.SAFE_DISTANCE(my_future_pos, future_pos):
                        #debug
                        print "COLLISION DETECTED:", dt, "  Critical:", dt > utils.COLLISION_CRITICAL
                        print "my_vals:", my_vals, "      my_v:", (my_vals[3], my_vals[4])
                        print "me:",my_future_pos, "\nother:",future_pos

                        if car_name not in self._collisions:
                            if dt > utils.COLLISION_CRITICAL:
                                self._collisions[car_name] = Collision(car_name, curr_frame + dt, 
                                    utils.CENTER_POINT(my_future_pos, future_pos))
                            else:
                                self._collisions[car_name] = Collision(car_name, curr_frame + dt, 
                                    utils.CENTER_POINT(my_future_pos, future_pos), critical=True)
                        else:
                            if dt <= utils.COLLISION_CRITICAL:
                                self._collisions[car_name].lock.acquire()
                                self._collisions[car_name].critical = True
                                self._collisions[car_name].lock.release()

    def _process_messages(self):
        """
        Message Processor:
            - processes incoming messages from CarTalker
            - creates collision objects and adds them to collisions
        """

        while not self._kill:
            message = self._talker.get_message()
            if message is None:
                continue

            if message.other_name not in self._collisions:
                if message.type != Message.ROW:
                    print "WE'RE FUCKED"
                    # TODO handle this
                else:
                    message.my_name = self.car_name
                    self._collisions[message.other_name] = Collision(message.other_name, message.frame_num,
                        message.location, message=message)
            else:
                collision = self._collisions[message.other_name]
                collision.lock.acquire()

                if message.type == Message.ROW:
                    if collision.state == CollisionState.WAITING:
                        # we are already waiting, so just send a confirmation that other has ROW
                        print "ALREADY WAITING"
                        self._talker.send_message(Message(Message.GO, self.car_name, message.other_name,
                            collision.location, collision.frame_num))

                    elif collision.state == CollisionState.RESOLVED:
                        # we are already going, so send a stay message
                        print "ALREADY RESOLVED"
                        self._talker.send_message(Message(Message.STAY, self.car_name, message.other_name,
                            collision.location, collision.frame_num))

                    elif collision.state == CollisionState.NEW:
                        # if we haven't already sent a message, set collision to received in interim
                        collision.state = CollisionState.RECEIVED_MESSAGE
                        message.my_name = self.car_name
                        collision.message = message

                    # TODO if we sent a message, need to resolve consensus issue (use frame num)
                    elif collision == CollisionState.SENT_MESSAGE:
                        if message.frame_num > collision.frame_num:
                            pass
                else:
                    if collision.state == CollisionState.SENT_MESSAGE:
                        if message.type == Message.STAY:
                            collision.state = CollisionState.WAITING
                            collision.message = None
                        else:
                            collision.state = CollisionState.RESOLVED
                            collision.message = None
                    else:
                        print "WE'RE FUCKED #2"
                        # TODO

                collision.lock.release()

            time.sleep(utils.THREAD_SLEEP)


    def _process_collisions(self):
        """
        Collision Processor:
            - main loop
            - drives car
            - processes Collision objects and decides course of action
            - constructs messages to other cars
        """

        while not self._kill:
            for car_name, collision in self._collisions.iteritems():
                # TODO might need this not to block so we can keep moving
                collision.lock.acquire()

                if collision.critical:
                    # stop driver, send ROW
                    self._driver.stop()
                    self.state = CarState.STOPPED
                    self._talker.send_message(Message(Message.ROW, self.car_name, collision.car_name,
                        collision.location, collision.frame_num, priority_val=_generate_priority()))
                    collision.state = CollisionState.SENT_MESSAGE

                else:
                    if collision.state == CollisionState.SENT_MESSAGE:
                        pass # just wait for reply

                    elif collision.state == CollisionState.WAITING:
                        self._driver.stop() # repeated calls are benign
                        self.state = CarState.STOPPED

                    elif collision.state == CollisionState.RESOLVED:
                        self._driver.go() # repated calls are benign
                        self._state = CarState.DRIVING

                    elif collision.state == CollisionState.NEW:
                        # send ROW
                        self._talker.send_message(Message(Message.ROW, self.car_name, collision.car_name,
                            collision.location, collision.frame_num, priority_val=_generate_priority()))
                        collision.state

                    elif collision.state == CollisionState.RECEIVED_MESSAGE:
                        assert collision.message != None
                        # process collision message

                        if collision.message == Messsage.ROW:
                            if message.priority_val > _generate_priority():
                                # send GO, wait
                                self._talker.send_message(Message.GO, self.car_name, message.other_name, collision.location,
                                    collision.frame_num)
                                collision.state = CollisionState.WAITING

                            else:
                                # send WAIT
                                self._talker.send_message(Message.STAY, self.car_name, message.other_name, collision.location,
                                    collision.frame_num)
                                collision.state = CollisionState.RESOLVED

                        elif collision.message == Messsage.GO:
                            collision.state = CollisionState.RESOLVED
                        else:
                            collision.state = CollisionState.WAITING

                collision.lock.release()

            time.sleep(utils.THREAD_SLEEP)

    @staticmethod
    def _generate_priority():
        return random.randint(0, utils.PRIORITY_CEILING)

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
    # testing
    car = Car()
    car._vicon_client.start()
    time.sleep(2)
    print "Running..."
    try:
        car._detect_collisions()
    except KeyboardInterrupt:
        pass
    # car = Car()
    # car.start()
    # print "Running..."
    # try:
    #     while(True):
    #         pass
    # except KeyboardInterrupt:
    #     pass
    # car.stop()

if __name__ == '__main__':
    main()
