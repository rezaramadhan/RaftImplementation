#!/usr/bin/python
"""high level support for doing this and that."""

import socket
import sys
import random
from threading import Thread
from config import *
from time import sleep

def appendEntries(term, leaderID, prefLogIdx, prefLogTerm, entries, leaderCommitIdx):
    if term < currentTerm:
        return (currentTerm, False)
    
    if prevLogIndex < len(log)
        entry = log[prevLogIndex]
        logTerm = entry["term"]
        
        if logTerm == prevLogTerm:
            log.append(entries)
            
            if commitIndex < leaderCommit:
                commitIndex = leaderCommit
                
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


def workerListener():
    sockServer = socket.socket()
    sockServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sockServer.bind((myhost, myport + 1))
    while True:
        try:
            sockServer.settimeout(WORKER_TIMEOUT)  # timeout for listening
            sockServer.listen(1)
            (conn, (ip, port)) = sockServer.accept()
            conn.setblocking(1)
            text = conn.recv(128)

        except socket.timeout:
            print "leader is dead"


def main(myhost, myport):
    """Main program entry point."""
    print "I'm " + myhost, myport
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
