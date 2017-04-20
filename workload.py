#!/usr/bin/env python
#from bs4 import BeautifulSoup

import psutil
import requests

cpu_workload = 0.0
loadBalancerList = []

def getLoadBalancerList(filename):
    with open(filename) as fp:
        for line in fp:
            loadBalancerList.append(line)

#Tentative, nanti ini dicari lagi
def getWorkLoad():
    cpu_workload = psutil.cpu_percent(interval=0.1)

def sendWorkload():
    for url in loadBalancerList:
        r = requests.post(url, data={'cpu_workload' : cpu_workload})
        print(r.status_code, r.reason)

getLoadBalancerList('loadbalancer.txt')
sendWorkload()
#for i in range(0, 100):
    #getWorkLoad()
