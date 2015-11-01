import atexit
import json
import logging
import socket
import selectors

from multiprocessing import Pipe
from iptc import Rule, Chain, Table
from pk import common

logger = logging.getLogger(__name__)

class PkDaemon:

    host = "localhost"
    state = None
    service_port = None
    port_is_open = True
    selector = selectors.DefaultSelector()
    running = False
    runner = None

    def __init__(self, iptables=True):
        self.iptables = iptables

    def register(self, service_port, secret):
        self.service_port = service_port

        # Compute secret knock sequence and reserve knocking ports
        knock = common._make_knocks(secret)
        self._reserve(*knock)

        # Register finalizer that uninstalls iptables inbound rule below
        if self.iptables:
            atexit.register(self._unblock_port)

            # Install iptables rule to block TCP pakcets inbound to service port
            self._block_port()

    def _unblock_port(self):
        if not self.port_is_open:
            logger.info("Deleting iptables rule to DROP TCP:%s" % self.service_port)        
            chain, rule = self._build_iptables_rule()
            chain.delete_rule(rule)
            self.port_is_open = True
        else:
            logger.info("Svc port %s is already open" % self.service_port)

    def _block_port(self):
        logger.info("Creating iptables rule to DROP TCP:%s" % self.service_port)
        chain, rule = self._build_iptables_rule()

        logger.info("Installing iptables rule...")
        chain.insert_rule(rule)
        logger.info("Successfully installed iptables DROP TCP:%s" % self.service_port)
        self.port_is_open = False

    def _build_iptables_rule(self):
        rule = Rule()
        
        rule.protocol = "tcp"
        match = rule.create_match("tcp")
        match.dport = str(self.service_port)

        target = rule.create_target("DROP")

        chain = Chain(Table(Table.FILTER), "INPUT")
        return chain, rule

   
    def _reserve(self, *knocks):
        logger.info("Knock is %s. Reserving ports" % str(knocks))
        sockmap = {}
        for port in knocks:
            logger.debug("Reserving port %s" % port)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.host, port))
            sock.listen(1)
            sockmap[sock] = port

        self.state = KnockState(knocks, sockmap) 
        self._build_selector()

    def _build_selector(self):
        for sock, port in self.state.get_sockmap().items():
            self.selector.register(sock, selectors.EVENT_READ, self._knock_handler)

        self.stopper, recver = Pipe()
        self.selector.register(recver, selectors.EVENT_READ, self._stop_handler)

    def _stop_handler(self, p, mask):
        logger.info("STOP message received")
        self.running = False

    def _knock_handler(self, sock, mask):
        # TODO: something more efficient?
        conn, addr = sock.accept()
        if self.state.put(sock):

            # Unblock firewall to hidden service
            # TODO: timeout/heartbeat until we shut again
            self._unblock_port()

            # Send port for hidden service to client
            resp = json.dumps(dict(port=self.service_port)).encode('utf8')
            conn.sendall(resp)


        conn.close()

    def stop(self):
        logger.info("Sending STOP message to server")
        self.stopper.send("stop".encode('utf8'))

    def start(self):
        self.running = True
        self.runner = common.on_thread(self.run)

    def run(self):
        while self.running:
            events = self.selector.select()
            for key, mask in events:
                cb = key.data
                cb(key.fileobj, mask)

# TODO: multiplex state by client addr
class KnockState:
    
    def __init__(self, knock, sockmap):
        self.knock = knock
        self.sockmap = sockmap
        self._ix = 0

    def put(self, sock):
        k = self.sockmap[sock]
        logger.debug("Knock on port %s" % k)
        if self.knock[self._ix] != k:
            logger.debug("Wrong knock, resetting")
            self._ix = 0
            return False
        elif self._ix == len(self.knock) - 1:
            logger.debug("Correct, sequence complete")
            return True
        else:
            self._ix += 1
            logger.debug("Correct, advancing to knock %s/%s" % (self._ix, len(self.knock)))
            return False

    def get_sockmap(self):
        return self.sockmap
