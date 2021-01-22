#!/usr/bin/python

import socket
import time
import sys
import argparse
import threading

parser = argparse.ArgumentParser()
parser.add_argument('-l', action='store_true')
parser.add_argument('-i', '--input')
parser.add_argument('-d', '--delay', type=float)
parser.add_argument('server')
parser.add_argument('port', type=int, nargs='?')
args = parser.parse_args()

s = socket.socket()
threadPool = []

def b2s(data):
	return str(data,'utf-8')

def reader(conn):
	try:
		data = conn.recv(2048)
		while data:
			print(b2s(data).rstrip('\n'))
			sys.stdout.flush()
			data = conn.recv(2048)
	except BrokenPipeError:
		conn.close()

def writer(conn):
	try:
		while True:
			start = 0
			data = sys.stdin.readline()
			sys.stdin.flush()
			if not send(conn, data):
				break
	except BrokenPipeError:
		conn.close()

def send(conn, data):
	start = 0
	sent = conn.send(bytes(data[start:],'utf-8'))
	while sent < len(data[start:]) and sent:
		start += sent
		sent = conn.send(bytes(data[start:],'utf-8'))
	return sent

def main():
	if args.l:
		s.bind(('localhost',int(args.server)))
		s.listen()
		#client_socket,client_address = s.accept()

		try:
			while True:
				client_socket,client_address = s.accept()
				print('Connection received from {0} port {1}'.format(client_address[0], client_address[1]),file=sys.stderr)
				writerThread = threading.Thread(target=writer, args=[client_socket],daemon=True)
				readerThread = threading.Thread(target=reader, args=[client_socket],daemon=True)
				writerThread.start()
				readerThread.start()
		except KeyboardInterrupt:
			client_socket.close()
			s.close()

	else:
		if args.port == None:
			print('Usage: ' + sys.argv[0] + ' <server> <port>')
			s.close()
			exit()


		address = (args.server,args.port)

		s.connect(address)
		print('Connected to {0} port {1}'.format(args.server, args.port), file=sys.stderr)
		sys.stdout.flush()
		readerThread = threading.Thread(target=reader,args=[s],daemon=True)
		threadPool.append(readerThread)
		readerThread.start()

		try:
			if args.input:
				f = open(args.input)
				data = f.readline()
				while data != '':
					if not send(s, data):
						break
					if args.delay:
						time.sleep(args.delay)
					data = f.readline()
			else:
				data = sys.stdin.readline()
				sys.stdin.flush()
				while send(s, data):
					if args.delay:
						time.sleep(args.delay)
					data = sys.stdin.readline()
					sys.stdin.flush()
		except KeyboardInterrupt:
			s.close()

	s.close()

main()
