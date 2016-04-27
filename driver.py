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

    def drive_path(self):
        # apply turn first
        if self.path[1] != None:
            GPIO.output(self.path[1], True)
        
        if self.path[0] != None:
            GPIO.output(self.path[0], True)

    def straighten(self):
        GPIO.output(self.path[1], False)
        self.path = (self.path[0], None)

    def turn_opposite(self, direction):
        if self.path[1] != None:
            GPIO.output(self.path[1], False)

        GPIO.output(direction, True)
        self.path = (self.path[0], direction)

    def forward(self):
        if self.path[0] == Direction.Back:
            GPIO.output(self.path[0], False)

        GPIO.output(Direction.Forward, True)
        self.path = (Direction.Forward, self.path[1])

    def reverse(self):
        if self.path[0] == Direction.Forward:
            GPIO.output(self.path[0], False)

        GPIO.output(Direction.Back, True)
        self.path = (Direction.Back, self.path[1])

    def stop(self):
        for pin in PINS:
            GPIO.output(pin, False)

        self.path = (None, None)

    def destroy(self):
        GPIO.cleanup()
        self.path = (None, None)
