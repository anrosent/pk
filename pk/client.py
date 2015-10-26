import logging
import json

from pk import common

logger = logging.getLogger(__name__)

class PkClient:

    def __init__(self, host, secret, n_knocks=4, port_range=(10000, 11000)):
        self.host = host
        self.secret = secret
        self.n_knocks = n_knocks
        self.port_range = port_range
        self.knocks = common._make_knocks(secret, n_knocks, port_range)

    def connect(self):
        for ix, k in enumerate(self.knocks):

            sock = self._connect_single(k)

            # look for message on last knock
            if ix == len(self.knocks) - 1:
                data = json.loads(sock.recv(1024).decode('utf8'))
                service_port = data['port']
                
        return common.sock_open(self.host, service_port)

    def _connect_single(self, k):
        logger.debug("Knocking (%s,%s)" % (self.host, k))
        return common.sock_open(self.host, k)

    def get_knocks(self):
        return self.knocks
