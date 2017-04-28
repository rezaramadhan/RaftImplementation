#!/usr/bin/python
"""high level support for doing this and that."""

import socket
import sys
import random
import json
import os.path
from threading import Thread
from config import *
from time import sleep

def appendEntries(term, leaderID, prevLogIdx, prevLogTerm, entries, leaderCommitIdx):
    term = int(term)
    leaderID = int(leaderID)
    prevLogIdx = int(prevLogIdx)
    prevLogTerm = int(prevLogTerm)
    leaderCommitIdx = int(leaderCommitIdx)
    
    if term < currentTerm:
        return (currentTerm, False)
    
    if prevLogIdx < len(log):
        entry = log[prevLogIdx]
        logTerm = entry["term"]
        
        if logTerm == prevLogTerm:
            print log
            log = log[:(prevLogIndex+1)] + entries
            print log
            
            if commitIndex < leaderCommitIdx:
                commitIndex = leaderCommitIdx
                
            return (currentTerm, True)
    
    return (currentTerm, False)


def sendHeartbeat(dest_host, dest_port):
    """Sending heartbeat to a single follower using a certain socket Client."""
    try:
        sockClient = socket.socket()
        sockClient.connect((dest_host, dest_port))
        print "->send ! to" + dest_host, dest_port
        sockClient.send("!" + str(term))
        sockClient.close()
    except socket.error, v:
        errorcode = v[0]
        if errorcode == socket.errno.ECONNREFUSED:
            print "!!Connection Refused"


def broadcastHeartbeat(myhost, myport):
    """Used by leader to broadcast heartbeat every HEARTBEAT_SEND_S."""
    while (state == "LEADER"):
        print "I'm a leader"
        jobs = []
        for follower in LOAD_BALANCER:
            if (follower[0] != myhost and follower[1] != myport):
                t = Thread(target=sendHeartbeat,
                           args=(follower[0], follower[1] + 1))
                jobs.append(t)
                t.start()

        # Wait for each thread to finish sending
        for job in jobs:
            job.join()
        sleep(HEARTBEAT_SEND_S)
    print "   now I'm not a leader"


def listenHeartbeat(myhost, myport):
    """Used by Follower to listen heartbeat from Leader."""
    sockServer = socket.socket()
    sockServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sockServer.bind((myhost, myport + 1))
    print "I'm a folllower"
    print "  Creating heartbeat listener on " + myhost, myport + 1

    isAlreadyVote = False
    global state
    while (state == "FOLLOWER"):
        # print "I'm a folllower"
        try:
            # random timeout between X and 2X
            heartbeatTimeout = random.uniform(HEARTBEAT_TIMEOUT_BASE_S,
                                              HEARTBEAT_TIMEOUT_BASE_S * 2)
            print "--current timeout " + str(heartbeatTimeout)
            sockServer.settimeout(heartbeatTimeout)  # timeout for listening
            sockServer.listen(1)
            (conn, (ip, port)) = sockServer.accept()
            conn.setblocking(1)
            text = conn.recv(128)
            print "<-recv " + text + "from" + ip, port
            global term
            if (text[0] == "!"):
                print "!-leader is alive"
                if (term != int(text.split('!')[1])):
                    term = int(text.split('!')[1])
                    isAlreadyVote = False
            elif (text == "request_vote"):
                if (isAlreadyVote):
                    print "->send no to" + ip, port
                    conn.send("no")
                else:
                    print "->send yes to" + ip, port
                    conn.send("yes")
                    isAlreadyVote = True
            conn.close()
        except socket.timeout:
            print "leader is dead"
            state = "CANDIDATE"
#    sockServer.shutdown(socket.SHUT_RDWR)
    print "   now I'm not a follower"


def askVote(myhost, myport):
    """Used by candidate to ask vote as a leader."""
    print "I'm a candidate"
    majorityVote = len(LOAD_BALANCER) / 2 + 1
    agreedVote = 1
    print myhost, myport
    for follower in LOAD_BALANCER:
        print follower
        if (follower[0] != myhost and follower[1] != myport):
            try:
                sockClient = socket.socket()
                sockClient.connect((follower[0], follower[1] + 1))
                print "->requesting vote to" + follower[0], follower[1] + 1
                sockClient.send("request_vote")
                data = sockClient.recv(128)
                print "<-recv " + data + " frm " + follower[0], follower[1] + 1
                if (data == "yes"):
                    agreedVote += 1
                sockClient.close()
            except socket.error, v:
                errorcode = v[0]
                if errorcode == socket.errno.ECONNREFUSED:
                    print "!!Connection Refused"
        else:
            print "It's me"
    global state
    print "  recvd vote " + str(agreedVote)
    if agreedVote >= majorityVote:
        state = "LEADER"
        global term
        term += 1
    else:
        state = "FOLLOWER"
    print "   now I'm not a candidate"


def workerListener(myhost, myport):
    sockServer = socket.socket()
    sockServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sockServer.bind((myhost, myport - 1))
    print "  Creating worker listener on " + myhost, myport - 1    
    while True:
        try:
            #sockServer.settimeout(WORKER_TIMEOUT)  # timeout for listening
            sockServer.listen(1)
            (conn, (ip, port)) = sockServer.accept()
            conn.setblocking(1)
            text = conn.recv(128)
            text = text.split(";")
            print "<-   recv from daemon " + text[0] + " " + text[1] + " from " + ip, port
            logElement = LogElement(currentTerm, text[0], (ip,text[1]))
            log.append(logElement)
            print log
            conn.close()

            file = open("log.txt","w") 
             
            file.write(str(currentTerm))
            file.write("|")
            file.write(str(votedFor))
            file.write("|")
            file.write(str(log))
            file.close() 
        except socket.timeout:
            print "leader is dead"

def getLowestDaemon():
    lowestDaemon = None
    lowestValue = 9999
    
    for key in server_list:
        if(lowestDaemon == None):
            lowestDaemon = key
            lowestValue = server_list[key]
        elif(server_list[key] < lowestValue):
            lowestDaemon = key
            lowestValue = server_list[key]
    
    return lowestDaemon
            
def loadLog(filename):
    # Check whether the file exist or not
    if(os.path.isfile(filename)):
        file = open(filename, "r")
         
        text = file.read()
        text = text.split("|")
        
        # Check whether the file empty or not
        if(len(text) != 0):
            currentTerm = int(text[0])
            if(text[0] != "None"):
                votedFor = text[0]
            logTemp = json.loads(text[2])
            
            for data in logTemp:
                logElement = LogElement(data['term'], data['load'], data['owner'])
                log.append(logElement)
            
            for data in log:
                server_list[str(data.owner)] = str(data.load)
            
            #print server_list
        
            
            
def main(myhost, myport):
    """Main program entry point."""
    print "I'm " + myhost, myport
    
    # Load existing log
    loadLog('log.txt')
    
    # Start thread to listen from daemon
    t = Thread(target=workerListener,
               args=(myhost, myport))
    t.start()
    
    while True:
        if (state == "FOLLOWER"):
            listenHeartbeat(myhost, myport)
        elif (state == "CANDIDATE"):
            askVote(myhost, myport)
        elif (state == "LEADER"):
            broadcastHeartbeat(myhost, myport)
        print


if __name__ == '__main__':
    if (len(sys.argv) != 2):
        print("Invalid Argument to start the file\n")
    else:
        main('', int(sys.argv[1]))
