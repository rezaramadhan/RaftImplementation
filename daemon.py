#!/usr/bin/env python
import socket
import psutil
import requests
import sys
from config import *
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
            print "->send ! to" + dest_host, dest_port
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
    sleep(15)
