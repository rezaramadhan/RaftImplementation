#!/usr/bin/env python

# Nama file : daemon.py
# Anggota :
#   1. Geraldi Dzakwan (13514065)
#   2. Ade Yusuf Rahardian (13514079)
#   3. Muhammad Reza Ramadhan (13514107)

"""IMPLEMENTASI RAFT - DAEMON."""
import socket
import psutil
import sys
from config import WORKER_SEND_S, LOAD_BALANCER
from time import sleep

cpu_workload = '0.0'
loadBalancerList = []

# Run with host name and port number argument
# Example : python daemon.py 8080
PORT_NUMBER = sys.argv[1]

def getWorkLoad():
    """ Get current workload """
    cpu_workload = str(psutil.cpu_percent(interval=0.1))
    return cpu_workload


def sendWorkload(workload):
    """ Send workload for all Load Balancer """
    for url in LOAD_BALANCER:
        try:
            dest_host = url[0]
            dest_port = int(url[1]) - 1
            print str(dest_host) + " " + str(dest_port)
            sockClient = socket.socket()
            sockClient.connect((dest_host, dest_port))
            sockClient.send(str(workload)+";"+PORT_NUMBER)
            sockClient.close()
        except socket.error, v:
            errorcode = v[0]
            if errorcode == socket.errno.ECONNREFUSED:
                print "!!Connection Refused"


while True:
    workload = getWorkLoad()
    print(str(workload))
    sendWorkload(workload)
    sleep(WORKER_SEND_S)
