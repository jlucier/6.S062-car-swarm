import RPi.GPIO as GPIO

class Direction(object):
    Forward = 29
    Back = 31
    Left = 33
    Right = 35
    Pins = [Forward, Back, Left, Right]

class Preset(object):
    ClockwiseCircle = (Direction.Forward, Direction.Right)
    CounterClockwiseCircle = (Direction.Forward, Direction.Left)

class Driver(object):

    def __init__(self, path=Preset.ClockwiseCircle):
        GPIO.setmode(GPIO.BOARD)
        for pin in Direction.Pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, False)

        self.path = path # (forward/back, turn)
        self.state = (None, None)

    def set_path(self, path):
        self.path = path

    def go(self):
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
        if self.state[0] == Direction.Back:
            GPIO.output(self.state[0], False)

        GPIO.output(Direction.Forward, True)
        self.state = (Direction.Forward, self.state[1])

    def reverse(self):
        if self.state[0] == Direction.Forward:
            GPIO.output(self.state[0], False)

        GPIO.output(Direction.Back, True)
        self.state = (Direction.Back, self.state[1])

    def stop(self):
        for pin in Direction.Pins:
            GPIO.output(pin, False)

        self.state = (None, None)

    def destroy(self):
        GPIO.cleanup()
        self.path = (None, None)
