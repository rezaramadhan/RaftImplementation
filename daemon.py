#!/usr/bin/env python
import psutil
import requests
import sys

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

def sendWorkload():
    for url in loadBalancerList:
        #r = requests.post(url, data={'cpu_workload' : cpu_workload})
        r = requests.get(url + '/' + HOST_NAME + '/' + PORT_NUMBER + '/' + cpu_workload)
        print(r.status_code, r.reason)

getLoadBalancerList('loadbalancer.txt')
sendWorkload()
#for i in range(0, 1):
    #getWorkLoad()
