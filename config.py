# Nama file : config.py
# Anggota :
#   1. Geraldi Dzakwan (13514065)
#   2. Ade Yusuf Rahardian (13514079)
#   3. Muhammad Reza Ramadhan (13514107)

"""IMPLEMENTASI RAFT - CONFIG."""

from ast import literal_eval

LOAD_BALANCER = [
    # ['127.0.0.1', 5000],
    # ['127.0.0.1', 6000],
    # ['127.0.0.1', 7000],
    ['192.168.43.52', 5000],
    ['192.168.43.52', 6000],
    ['192.168.43.52', 7000]
]

# Avaiable state = [FOLLOWER, LEADER, CANDIDATE]
state = "FOLLOWER"
HEARTBEAT_SEND_S = 3
HEARTBEAT_TIMEOUT_BASE_S = HEARTBEAT_SEND_S * 2
WORKER_SEND_S = 10
server_list = {}


""" Persistent state on all servers """
currentTerm = 0
votedFor = -1
log = []

""" Volatile state on all servers """
commitIndex = 0
lastApplied = -1

""" Volatile state on leaders """
nextIndex = []
matchIndex = []


class LogElement():
    """Log element Class."""

    def __init__(self, term=0, load=0.0, owner=(1, 1)):
        """constructor."""
        self.term = term
        self.load = float(load)
        if (isinstance(owner, basestring)):
            self.owner = literal_eval(owner)
        else:
            self.owner = owner

    def setDict(self, dict):
        self.term = dict["term"]
        self.load = float(dict["load"])
        self.owner = literal_eval(dict["owner"])

    def toString(self):
        """Tostring method."""
        data = ('{ "term" : "' + str(self.term) +
                '", "load" : "' + str(self.load) +
                '", "owner" : "' + str(self.owner) + '" }')
        return data

    def __repr__(self):
        """Tostring method."""
        data = ('{ "term" : "' + str(self.term) +
                '", "load" : "' + str(self.load) +
                '", "owner" : "' + str(self.owner) + '" }')
        return data
