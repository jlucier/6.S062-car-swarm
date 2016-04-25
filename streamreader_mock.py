import time, random

FRAME_NUM = 0

'''
	Mock streamreader API for testing
'''

def connect(ip):
	return True

def get_frame():
	global FRAME_NUM
	FRAME_NUM += 1
	time.sleep(.25)
	return {'car_test1':(random.uniform(0, 100), random.uniform(100,200), random.random(), FRAME_NUM),
			'car_test2':(-random.uniform(0,200), -random.uniform(0, 100), random.uniform(1,2), FRAME_NUM)}