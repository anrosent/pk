import json
import logging
import socket
import selectors

from multiprocessing import Pipe
from pk import common

logger = logging.getLogger(__name__)

class PortKnockerManager:

    host = "localhost"
    state = None
    service_port = None
    selector = selectors.DefaultSelector()
    running = False
    runner = None

    def register(self, service_port, secret, n_knocks=4, port_range=(10000,11000)):
        self.service_port = service_port
        knock = common._make_knocks(secret, n_knocks, port_range)
        self._reserve(*knock)
   
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
        # if we get any other connects in the port range, reset (range should be small then)

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
