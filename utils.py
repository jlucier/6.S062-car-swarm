import json, urllib2
import socket
import os

# Defines configuration details and helper functions

# Vicon Streaming server config
SERVER_PORT = 4001
SERVER_NAME = "vicon_server"
VICON_PORT = 801
VICON_HOST = '192.168.20.99'

API_URL_ADD = 'http://54.173.46.77/add'
API_URL_GET = 'http://54.173.46.77/get'

NAME_FILE = os.path.expanduser('~')+'/car_name.txt'

def get_car_ips():
	req = urllib2.Request(API_URL_GET)
	return json.loads(urllib2.urlopen(req))

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def send_ip(name, ip_address):
	headers = {'IP': str(ip_address), 'NAME': str(name)}
	req = urllib2.Request(API_URL_ADD, headers=headers)
	return json.load(urllib2.urlopen(req))['result'] == 'success'
