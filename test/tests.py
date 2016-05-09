import sys
sys.path.append('../dir')

from car import Car

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
	car = Car()
	car.start()
	try:
		raw_input("Running... press any button to stop")
	except KeyboardInterrupt:
		pass
	car.stop()
	print "Done"

def main(argv):
	if len(argv) < 2:
		test_system()
	elif argv[1] == 'collisions':
		test_collision()
	else
		print "Usage: collisions / cp / mp"

if __name__ == '__main__':
	main()