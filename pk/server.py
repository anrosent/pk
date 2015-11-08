import atexit
import json
import logging
import socket
import selectors

from multiprocessing import Pipe
from pk import common
from pk import firewall
from pk import knock

logger = logging.getLogger(__name__)

class PkDaemon:

    host = "localhost"
    state = None
    service_port = None
    port_is_open = True
    selector = selectors.DefaultSelector()
    running = False
    runner = None
    sockets = []

    def __init__(self, iptables=True):
        if iptables:
            self.firewall = firewall.IptablesFirewall()
        else:
            self.firewall = firewall.DummyFirewall()

    def register(self, service_port, secret):
        self.service_port = service_port

        # Compute secret knock sequence and reserve knocking ports
        knock = common._make_knocks(secret)
        self._reserve(*knock)

        # Register finalizer that uninstalls iptables inbound rule below
        atexit.register(self.firewall.clear)

        # Install iptables rule to block TCP pakcets inbound to service port
        self.firewall.block_all(service_port)

    def _reserve(self, *knocks):
        logger.info("Knock is %s. Reserving ports" % str(knocks))
        for port in knocks:
            logger.debug("Reserving port %s" % port)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.host, port))
            sock.listen(1)
            self.sockets.append(sock)

        self.state = knock.KnockMuxer(knocks) 
        self._build_selector()

    def _build_selector(self):
        for sock in self.sockets:
            self.selector.register(sock, selectors.EVENT_READ, self._knock_handler)

        self.stopper, recver = Pipe()
        self.selector.register(recver, selectors.EVENT_READ, self._stop_handler)

    def _stop_handler(self, p, mask):
        logger.info("STOP message received")
        self.running = False

    def _knock_handler(self, sock, mask):
        # TODO: something more efficient?
        conn, addr = sock.accept()
        client = conn.getpeername()
        localaddr = sock.getsockname()
        if self.state.put(localaddr, client):

            # Unblock firewall to hidden service for this client
            # TODO: timeout/heartbeat until we shut again
            self.firewall.unblock(self.service_port, client)

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

