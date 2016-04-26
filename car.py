import random as rand
import time
import math
from collections import deque

class Car(object):
    
    name = "car"
    
    #POSITION AND TIME TRACKING QUEUES
    xpos = deque(maxlen = 2500)     #index -1 is most recent in time
    ypos = deque(maxlen = 2500)     #index -1 is most recent in time
    theta = deque(maxlen = 2500)    #index -1 is most recent in time
    time = deque(maxlen = 2500)     #index -1 is most recent in time
    velocity = deque(maxlen = 2500) #index -1 is most recent in time

    send_time = 0
    sent = False
    otherCars = {}
    maxVelocity = 1
    # The class "constructor" - It's actually an initializer 
    def __init__(self, name):
        self.name = name
    
    def collision_detection(self, CarTwo): #should be ran 2-20Hz
        distanceThreshold = 1

        distanceSquared = (self.xpos[0] - CarTwo.xpos[0])**2 
                        + (self.ypos[0] - CarTwo.ypos[0])**2
        if (math.sqrt(distanceSquared) < distanceThreshold):
            collision_resolution(self, CarTwo)

    def collision_resolution(self, CarTwo):
        self.resolved = False
        while(self.resolved == False):
            randomized_send(self, CarTwo)
    
    def randomized_send(self, CarTwo):
        timeout = (rand.random())/100 #rand between [0, 10] milliseconds
        time.sleep(timeout) #randomized timeout akin to CSMA

        #SEND message (STOP, current_time) to other Car

        self.send_time = time.clock()
        self.sent = True
    
    def send_message(msg):
        #TODO IMPLEMENT
    def drive(maxVelocity):
        #TODO IMPLEMENT
    
    def integrate_frame(frame):
        self.xpos.append(frame.x)
        self.ypos.append(frame.y)
        self.theta.append(frame.z)
        self.time.append(frame.t)

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


