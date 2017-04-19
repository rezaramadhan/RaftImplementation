#!/usr/bin/env python
import psutil

def getWorkLoad():
    print(psutil.cpu_percent(interval=0.1))

for i in range(0, 100):
    getWorkLoad()
