#!/usr/bin/env python

import socket, fcntl, sys

#Lock to only allow one instance of this program to run
pid_file = '/tmp/send.pid'
fp = open(pid_file, 'w')
try:
   fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
except IOError:
   print 'An instance of this program is already running'
   sys.exit(0)

import Adafruit_CharLCD as LCD

lcd = LCD.Adafruit_CharLCDPlate()
lcd.set_color(0,0,0)

listener = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)

number_packets_received = 0

def print_lcd():
   lcd.clear()
   lcd.message('# of packets\nreceived: ' + str(number_packets_received))

if __name__ == '__main__':
   while True:
      print_lcd()
      print listener.recvfrom(7777)
      number_packets_received += 1
