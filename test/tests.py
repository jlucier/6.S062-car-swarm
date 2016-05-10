import sys
sys.path.append('../')

from car import Car
from driver import Preset

def test_collisions():
    car = Car()
    car._vicon_client.start()
    time.sleep(2)
    print "Running..."
    try:
        car._detect_collisions()
    except KeyboardInterrupt:
        car._kill = True
        time.sleep(.5)
    print "Done"

def test_system():
    straight = raw_input("Drive straight? ")
    path = Preset.STRAIGHT if straight == 'y' else None
    if not path:
        path = Preset.COUNTER_CLOCKWISE_CIRCLE if raw_input("Counter clockwise? ") == 'y' else path
    car = Car(path=path)
    car.start()
    try:
        raw_input("Running... press enter to start driving\n")
        car._driver.go()
        raw_input('Press enter to stop...')
    except KeyboardInterrupt:
        pass
    car.stop()
    print "Done"

def test_bystander():
    # no collision detection
    car = Car()
    car._vicon_client.start()
    car._talker.start()
    car._message_worker.start()
    car._main_worker.start()

    try:
        raw_input("Running... press enter to stop\n")
    except KeyboardInterrupt:
        pass

    car._driver.stop()
    car._driver.destroy()
    car._kill = True
    car._vicon_client.stop()
    car._talker.stop()
    car._message_worker.join()
    car._main_worker.join()
    print "Done"

def main():
    if len(sys.argv) < 2:
        test_system()
    elif sys.argv[1] == 'collisions':
        test_collision()
    elif sys.argv[1] == 'bystander':
        test_bystander()
    else:
        print "Usage: collisions / cp / mp"

if __name__ == '__main__':
    main()