"""Raft configuration."""
LOAD_BALANCER = [
    ['127.0.0.1', 5000],
    ['127.0.0.1', 6000],
    ['127.0.0.1', 7000]
    # ['127.0.0.1', 8000],
    # ['127.0.0.1', 9000]
]

# Avaiable state = [FOLLOWER, LEADER, CANDIDATE]
state = "FOLLOWER"
term = 1
# HEARTBEAT_SEND_S = 0.05
# HEARTBEAT_TIMEOUT_BASE_S = HEARTBEAT_SEND_S
HEARTBEAT_SEND_S = 2
HEARTBEAT_TIMEOUT_BASE_S = HEARTBEAT_SEND_S * 2
WORKER_TIMEOUT = 5
server_list = {}


""" Persistent state on all servers """"
currentTerm = 0
votedFor = null
log = []

""" Volatile state on all servers """
commitIndex = -1
lastApplied = -1

""" Volatile state on leaders """
nextIndex = []
matchIndex = []

class logElement():
    def __init__(term, load, owner):
        self.term = term
        self.load = 80
        self.owner = owner