import logging

import common

logger = logging.getLogger(__name__)

class PortKnock:

    def __init__(self, host, secret, n_knocks=4, port_range=(10000, 11000)):
        self.host = host
        self.secret = secret
        self.n_knocks = n_knocks
        self.port_range = port_range
        self.knocks = common._make_knocks(secret, n_knocks, port_range)

    def connect(self):
        for k in self.knocks:
            self._connect_single(k)

    def _connect_single(self, k):
        logger.debug("Kocking (%s,%s)" % (self.host, k))
        return common.sock_open((self.host, k))

    def get_knocks(self):
        return self.knocks
    # generate knocks
    # connect to host in order
    # timeout?
    # return socket at end (success message w/ port on final knock?)
