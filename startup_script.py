#!/usr/bin/env python

import time
import logging, logging.handlers

from utils import * # config and ip address functions

lpath = '/var/log/pi/'
logger = logging.getLogger('car_startup_script')
logger.setLevel(logging.DEBUG)
fh = logging.handlers.RotatingFileHandler('{}car_startup_script.log'.format(lpath))

fh.setLevel(logging.DEBUG)
frmt = logging.Formatter('%(asctime)s-%(levelname)s:%(message)s')
fh.setFormatter(frmt)
logger.addHandler(fh)

def main():
	logger.info('Starting script')
	fail = True
	ip_address = ''
	while(fail):
		try:
			ip_address = get_ip_address()
			fail = False
		except Exception as e:
			fail = True
			logger.info('Failed to acquire and ip... trying again in 1 second. Message: {}'.format(e.message))
			time.sleep(1)

	if ip_address is '' or ip_address is None:
		logger.info('No IP address found... terminating')
		return

	f = open(NAME_FILE, 'r')
	car_name = f.read().strip()
	f.close()

	response = send_ip(car_name, ip_address)

	if not response:
		logger.info('Failed to send IP to server')

	logger.info('Success ... terminating')

if __name__ == '__main__':
	main()