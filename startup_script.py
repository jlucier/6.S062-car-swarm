#!/usr/bin/env python

import os
import socket
import urllib2
import json
import logging, loggin.handlers

API_URL = 'http://54.173.46.77/add'
NAME_FILE = os.path.expanduser('~')+'/car_name.txt'

lpath = '/var/log/pi/'
logger = logging.getLogger('car_startup_script')
logger.setLevel(logging.DEBUG)
fh = logging.handlers.RotatingFileHandler('{}car_startup_script.log'.format(lpath))

fh.setLevel(logging.DEBUG)
frmt = logging.Formatter('%(asctime)s-%(levelname)s:%(message)s')
fh.setFormatter(frmt)
logger.addHandler(fh)

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def send_ip(name, ip_address):
	headers = {'IP': str(ip_address), 'NAME': str(name)}
	req = urllib2.Request(API_URL, headers=headers)
	return json.load(urllib2.urlopen(req))

def main():
	fail = True
	ip_address = ''
	while(fail):
		try:
			ip_address = get_ip_address()
			fail = False
		except:
			fail = True

	if ip_address is '' or ip_address is None:
		raise Exception('Failed to acquire IP Address')

	f = open(NAME_FILE, 'r')
	car_name = f.read().strip()
	f.close()

	response = send_ip(car_name, ip_address)

	if response.get('result') != 'success':
		raise Exception('Failed to send IP to server')

if __name__ == '__main__':
	main()