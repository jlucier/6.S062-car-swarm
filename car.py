import random as rand
import time
import math
from collections import deque

import utils
from viconclient import ViconClient

class Car(object):
    def __init__(self):
        f = open(utils.NAME_FILE, 'r')
        car_name = f.read().strip()
        f.close()

        self.name = car_name
        self.frames = deque(maxlen=5) # frame = {'car_name': (x,y,theta,v,t), ...}
        self._kill = False
        self._collision_worker = threading.Thread(target=self._detect_collisions)

        car_ips = dict()
        vicon_ip = None
        ips = get_car_ips()

        for name, ip in ips.iteritems():
            if name == utils.SERVER_NAME:
                vicon_ip = ip
            elif name != self.car_name:
                self._car_ips[name] = ip

        self._vicon_client = ViconClient(vicon_ip, utils.SERVER_PORT, self.frames)
        self._talker = CarTalker(car_ips)
    
    def _detect_collisions(self):
        while not self._kill:
            if len(self.frames) == 0:
                continue
            curr_frame = self.frames[-1]
            my_vals = curr_frame[self.car_name]

            for car_name, vals in curr_frame.iteritems():
                if car_name == self.car_name:
                    continue

                # look ahead to determine if they will collide (come within utils.MIN_DISTANCE)
                # based on orientation and velocity, not just distance

                if collide:
                    resolve_collision(self, car_name)

    def resolve_collision(self, other_car):
        self.resolved = False
        while(self.resolved == False):
            randomized_send(self, CarTwo)
    
    def randomized_send(self, CarTwo):
        timeout = (rand.random())/100 #rand between [0, 10] milliseconds
        time.sleep(timeout) #randomized timeout akin to CSMA

        #SEND message (STOP, current_time) to other Car

        self.send_time = time.clock()
        self.sent = True

    def start(self):
        self._vicon_client.start()
        self._talker.start()
        self._collision_worker.start()

    def stop(self):
        self._kill = False
        self._vicon_client.stop()
        self._talker.stop()
        self._collision_worker.join()
        return True

    def listen(self, message):
        #CAN ADD WHILE LOOP FOR ROBUSTNESS 

        if packet_received(): #TODO 
            if(message.timestamp<self.send_time || self.sent==False):
                reply(GO) #TODO
                self.drive(0) 
            elif(message=="ALL CLEAR"):
                self.resolved=True

            else:
                #wait for GO message THEN
                self.resolved = True
                self.drive(self.maxVelocity)
                wait(timeout) #time to be clear of other car
                reply(ALL CLEAR) 
            self.sent = False


