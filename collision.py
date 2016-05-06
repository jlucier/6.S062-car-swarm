import numpy as np
import threading

import utils

class CollisionState(object):
    NEW = 0                # brand new, no action taken
    SENT_MESSAGE = 1       # message sent, waiting for reply
    RECEIVED_MESSAGE = 1   # message received, need to reply
    WAITING = 3            # other car has right of way
    RESOLVED = 4           # collision resolved (we have ROW or done waiting), good to drive

class Collision(object):
    """
    Encapsulates collisions and their necessary information
    """

    def __init__(self, car_name, frame_num, location, state=CollisionState.NEW, message=None, critical=False):
        self.car_name = car_name
        self.frame_num = frame_num
        self.location = location
        self.state = state
        self.message = message
        self.critical = critical
        self.lock = threading.RLock()

    def safe_to_drive(self, other_car):
        """
        Determines if the collision is over and it will be safe to drive

        A collision is deemed "over" iff the distance between the car and the collision location is safe
        and the car is moving away from the location
        @param other_car: the values associated with the adversarial car from a frame => (x,y,theta,vx,vy,t)
        @return bool: true if safe, false otherwise
        """

        if not utils.SAFE_DISTANCE(self.location, (other_car[0], other_car[1])):
            return False

        car_pos = np.array([other_car[0], other_car[1]])
        car_vel = np.array([other_car[3], other_car[4]])
        l = np.array(self.location)
        c_to_l = np.subtract(l, car_pos)
        return np.dot(c_to_l, car_vel) < 0
