import RPi.GPIO as GPIO

class Direction(object):
    FORWARD = 29
    BACK = 31
    LEFT = 33
    RIGHT = 35
    PINS = [FORWARD, BACK, LEFT, RIGHT]

class Preset(object):
    CLOCKWISE_CIRCLE = (Direction.FORWARD, Direction.RIGHT)
    COUNTER_CLOCKWISE_CIRCLE = (Direction.FORWARD, Direction.LEFT)

class Driver(object):

    def __init__(self, path=Preset.CLOCKWISE_CIRCLE):
        GPIO.setmode(GPIO.BOARD)
        for pin in Direction.PINS:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, False)

        self.path = path # (forward/back, turn)
        self.state = (None, None)

    def set_path(self, path):
        self.path = path

    def go(self):
        if self.state == self.path:
            return

        # apply turn first
        if self.path[1] != None:
            GPIO.output(self.path[1], True)
        
        if self.path[0] != None:
            GPIO.output(self.path[0], True)

        self.state = self.path

    def straighten(self):
        GPIO.output(self.state[1], False)
        self.state = (self.state[0], None)

    def forward(self):
        if self.state[0] == Direction.BACK:
            GPIO.output(self.state[0], False)

        GPIO.output(Direction.FORWARD, True)
        self.state = (Direction.FORWARD, self.state[1])

    def reverse(self):
        if self.state[0] == Direction.FORWARD:
            GPIO.output(self.state[0], False)

        GPIO.output(Direction.BACK, True)
        self.state = (Direction.BACK, self.state[1])

    def stop(self):
        if self.state == (None, None):
            return

        for pin in Direction.PINS:
            GPIO.output(pin, False)

        self.state = (None, None)

    def destroy(self):
        GPIO.cleanup()
        self.state = (None, None)
        self.path = (None, None)
