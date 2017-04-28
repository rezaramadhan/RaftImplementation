#!/usr/bin/python

# Nama file : node.py
# Anggota :
#   1. Geraldi Dzakwan (13514065)
#   2. Ade Yusuf Rahardian (13514079)
#   3. Muhammad Reza Ramadhan (13514107)

"""IMPLEMENTASI RAFT - NODE."""

import json
import socket
import sys
import random
import json
import os.path
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import requests
from threading import Thread
from config import (LOAD_BALANCER, state, HEARTBEAT_SEND_S, server_list,
                    HEARTBEAT_TIMEOUT_BASE_S, WORKER_TIMEOUT,
                    currentTerm, votedFor, log, commitIndex, lastApplied,
                    nextIndex, matchIndex, LogElement)
from time import sleep

myID = 0
agreedLogNumber = 1


class LoadBalancerHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        # Don't change init order. If changed, exception is gonna happen
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def do_POST(self):
        try:
            print(self.request.get('cpu_workload'))
        except Exception as ex:
            self.send_response(500)
            self.end_headers()
            print(ex)

    def do_GET(self):
        try:
            args = self.path.split('/')
            if len(args) != 2:
                raise Exception()
            n = int(args[1])

            suitableWorker = getLowestDaemon()
            r = requests.get("http://"+str(suitableWorker[0])+":"+str(suitableWorker[1])+"/"+str(n))
            data = r.text
            self.send_response(200)
            self.end_headers()

            self.wfile.write(data.encode('utf-8'))
#
        except Exception as ex:
            self.send_response(500)
            self.end_headers()
            print(ex)


def appendEntries(term, leaderID, prevLogIdx, prevLogTerm, entries,
                  leaderCommitIdx, myhost, myport):
    """Append entries RPC."""
    global currentTerm, votedFor, commitIndex, log

    if (term > currentTerm):
        currentTerm = term
        votedFor = -1


    # Check if there's no entry in payload
    if len(entries) == 0:
        return (currentTerm, None)

    term = int(term)
    leaderID = int(leaderID)

    prevLogIdx = int(prevLogIdx)
    prevLogTerm = int(prevLogTerm)
    leaderCommitIdx = int(leaderCommitIdx)

    if term < currentTerm:
        print "!!!!!false wrongterm"
        return (currentTerm, False)

    # entry = log[prevLogIdx]
    # logTerm = entry.term

    # if logTerm == prevLogTerm:

    # Change payload data to LogElement
    new_entry = []
    global server_list
    for entry in entries:
        elmt = LogElement()
        elmt.setDict(entry)
        new_entry.append(elmt)
        server_list[elmt.owner] = elmt.load

    log = log[:(prevLogIdx+1)] + new_entry
    saveLog("log"+myhost+str(myport)+".txt")

    print
    print "__log__" + str(log)
    print

    if commitIndex < leaderCommitIdx:
        commitIndex = leaderCommitIdx

    return (currentTerm, True)


def processHearbeat(data, myhost, myport):
    """Used by follower to prcess a heartbeat payload."""
    # print "  processing data " + data
    body = json.loads(data)

    print "___added___" + str(body)
    print "___entries___" + str(body['entries'])
    print

    # Call appendEntries to handle payload
    (term, result) = appendEntries(body['term'], body['leaderID'],
                                   body['prefLogIdx'], body['prefLogTerm'],
                                   body['entries'], body['leaderCommitIdx'], myhost, myport)

    # Convert appendEntries return value to payload data
    data = '{"term" : ' + str(term) + ', "success" : "' + str(result) + '"}'
    return data


def createEntries(firstIdx, lastIdx):
    """Used by leader to convert log entries to json equivalent.
       The converted value will be sent through socket
    """
    print firstIdx, lastIdx

    if (firstIdx >= lastIdx or firstIdx < 0):
        return "[]"

    data = "[" + str(log[firstIdx])
    for i in range(firstIdx + 1, lastIdx):
        data = data + ", " + str(log[i])
    data = data + "]"
    return data


def sendHeartbeat(dest_host, dest_port, clientID):
    """Sending heartbeat to a single follower using a certain socket Client."""
    try:
        global currentTerm, log, commitIndex, nextIndex, agreedLogNumber

        sockClient = socket.socket()
        sockClient.connect((dest_host, dest_port))
        print "->send ! to" + dest_host, dest_port
        prefLogIdx = nextIndex[clientID] - 1
        entries = createEntries(nextIndex[clientID], len(log))
        # print entries
        if (len(log) != 0 and prefLogIdx != -1):
            term = log[prefLogIdx].term
        else:
            term = -1

        # Create payload data
        payloads = ('beat' + '{ '
                    '"term" : ' + str(currentTerm) + ","
                    '"leaderID" : ' + str(myID) + ","
                    '"prefLogIdx" : ' + str(prefLogIdx) + ","
                    '"prefLogTerm" : ' + str(term) + ","
                    '"entries" : ' + str(entries) + ","
                    '"leaderCommitIdx" : ' + str(commitIndex) +
                    '}')

        # print payloads
        sockClient.send(payloads)
        recvData = sockClient.recv(1024)
        print recvData
        body = json.loads(recvData)

        # Check result, add agreed commit and manage nextIndex
        if(body['success'] == 'True'):
            nextIndex[clientID] += 1
            agreedLogNumber += 1
        elif (body['success'] == "False"):
            nextIndex[clientID] -= 1
        print "__nextIDX__" + str(nextIndex)

        sockClient.close()
    except socket.error, v:
        errorcode = v[0]
        if errorcode == socket.errno.ECONNREFUSED:
            print "!!Connection Refused"


def broadcastHeartbeat(myhost, myport):
    global agreedLogNumber, commitIndex
    """Used by leader to broadcast heartbeat every HEARTBEAT_SEND_S."""

    while (state == "LEADER"):
        print "I'm a leader"
        jobs = []

        for follower in LOAD_BALANCER:
            if (follower[0] != myhost and follower[1] != myport):
                t = Thread(target=sendHeartbeat,
                           args=(follower[0], follower[1] + 1,
                                 LOAD_BALANCER.index(follower)))
                jobs.append(t)
                t.start()

        # Wait for each thread to finish sending
        for job in jobs:
            job.join()
        print "+++++++++agreed " + str(agreedLogNumber)

        # Check majority vote, commit if success
        if (agreedLogNumber >= len(LOAD_BALANCER) / 2 + 1):
            print "==============commit index"
            commitIndex += 1
        else:
            print "============notcommit"

        agreedLogNumber = 1
        sleep(HEARTBEAT_SEND_S)
    print "   now I'm not a leader"


def listenHeartbeat(myhost, myport):
    """Used by Follower to listen heartbeat from Leader."""
    sockServer = socket.socket()
    sockServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sockServer.bind((myhost, myport + 1))
    print "I'm a folllower"
    print "  Creating heartbeat listener on " + myhost, myport + 1

    global state
    while (state == "FOLLOWER"):
        # print "I'm a folllower"
        try:
            # random timeout between X and 2X
            heartbeatTimeout = random.uniform(HEARTBEAT_TIMEOUT_BASE_S,
                                              HEARTBEAT_TIMEOUT_BASE_S * 2)
            # print "--current timeout " + str(heartbeatTimeout)
            sockServer.settimeout(heartbeatTimeout)  # timeout for listening
            sockServer.listen(1)
            (conn, (ip, port)) = sockServer.accept()
            conn.setblocking(1)
            text = conn.recv(2048)

            # print "<-recv " + text + "from" + ip, port
            # global currentTerm
            if (text[0:4] == "beat"):
                # Manage heartbeat
                result = processHearbeat(text[4:], myhost, myport)
                conn.send(result)
            elif (text[0:3] == "req"):
                # requestVote management
                global votedFor
                if (votedFor != -1):
                    print "->send no to" + ip, port
                    conn.send("no")
                    print "   votedFor " + str(votedFor)
                else:
                    print "->send yes to" + ip, port
                    conn.send("yes")
                    votedFor = int(text.split('|')[1])
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

    # Ask vote to all load balancer
    for follower in LOAD_BALANCER:
        print follower
        if (follower[0] != myhost and follower[1] != myport):
            try
                sockClient = socket.socket()
                sockClient.connect((follower[0], follower[1] + 1))
                print "->requesting vote to" + follower[0], follower[1] + 1
                sockClient.send("req|" + str(myID))

                # Handle vote result
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

    # Check majority vote, become a leader if success
    if agreedVote >= majorityVote:
        state = "LEADER"
        global currentTerm
        currentTerm += 1
    else:
        state = "FOLLOWER"
    print "   now I'm not a candidate"


def workerListener(myhost, myport):
    """Listener for a worker cpu loads."""
    global server_list
    sockServer = socket.socket()
    sockServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sockServer.bind((myhost, myport - 1))
    print "  Creating worker listener on " + myhost, myport - 1
    while True:
        try:
            # sockServer.settimeout(WORKER_TIMEOUT)  # timeout for listening
            sockServer.listen(1)
            (conn, (ip, port)) = sockServer.accept()
            conn.setblocking(1)
            text = conn.recv(128)
            text = text.split(";")

            # Handle data from worker
            print "<-    recv from daemon " + text[0] + " " + text[1] + " from " + ip, port
            if (currentTerm > 0):
                logElement = LogElement(currentTerm, text[0], (ip, text[1]))
                log.append(logElement)
                saveLog("log" + myhost+str(myport)+".txt")
                server_list[(ip, text[1])] = text[0]
            # print log
            conn.close()

        except socket.timeout:
            print "leader is dead"


def printlog():
    data = ""
    for elmt in log:
        data = data + str(elmt) + ", "
    print "log = " + data


def initializeNextIndex():
    """Used by new leader each term to initialize next index."""
    global nextIndex
    nextIndex = []
    for i in range(0, len(LOAD_BALANCER)):
        nextIndex.append(len(log))


def getLowestDaemon():
    lowestDaemon = None
    lowestValue = 9999

    for key in server_list:
        if (lowestDaemon is None):
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

            # print server_list


def saveLog(filename):
    file = open(filename, "w")

    file.write(str(currentTerm))
    file.write("|")
    file.write(str(votedFor))
    file.write("|")
    file.write(str(log))
    file.close()


def main(myhost, myport):
    """Main program entry point."""
    print "I'm " + myhost, myport

    # Load existing log
    loadLog('log'+myhost+str(myport)+'.txt')

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
            initializeNextIndex()
            broadcastHeartbeat(myhost, myport)
        print


if __name__ == '__main__':
    if (len(sys.argv) != 2):
        print("Invalid Argument to start the file\n")
    else:
        myID = int(sys.argv[1])
        server = HTTPServer(('', LOAD_BALANCER[myID][1]), LoadBalancerHandler)
        print "@@@@@@@@@@@@@@@@@hello"

        t = Thread(target=server.serve_forever, args=())
        t.start()
        print "$$$$$$$$$$$$"
        main('', LOAD_BALANCER[myID][1])
