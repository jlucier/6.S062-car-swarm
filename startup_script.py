#!/usr/bin/env python

import socket

def get_ip_address():
    print socket.gethostbyname(socket.gethostname())

def main():
	fail = True
	ip_address = ''
	while(fail):
		try:
			ip_address = get_ip_address()
		except:
			pass

	if ip_address is '' or ip_address is None:
		


if __name__ == '__main__':
	main()