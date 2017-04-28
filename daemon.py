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
# Example : python daemon.py 127.0.0.1 8080 (just like worker)
HOST_NAME = sys.argv[1]
PORT_NUMBER = sys.argv[2]

def getLoadBalancerList(filename):
    with open(filename) as fp:
        for line in fp:
            loadBalancerList.append(line)

#Tentative, nanti ini dicari lagi
def getWorkLoad():
    cpu_workload = str(psutil.cpu_percent(interval=0.1))
    return cpu_workload

def sendWorkload(workload):
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

print "haha"
while True:
    workload = getWorkLoad()
    print(str(workload))
    sendWorkload(workload)
    sleep(5)