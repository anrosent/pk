import logging
import json
from collections import namedtuple

from pk import common

logger = logging.getLogger(__name__)

class PkClient:

    def __init__(self, host, secret):
        self.host = host
        self.secret = secret
        self.knocks = common._make_knocks(secret)
        self.localaddr = ("localhost", None)

    def connect(self):
        for ix, k in enumerate(self.knocks):
            sock = self._connect_single(k)

            # look for message on last knock
            if ix == len(self.knocks) - 1:
                logger.debug("Success! Receiving hidden service port")
                data = sock.recv(1024).decode('utf8')
                service_port = json.loads(data)['port']
                logger.info("Hidden service port is %s" % service_port)
            sock.close()

        return self._connect_single(service_port)

    def _connect_single(self, k):
        _, lport = self.localaddr
        logger.debug("Knocking (%s,%s)" % (self.host, k))
        if not lport:
            logger.debug("No client socket bound")
            sock = common.sock_open(self.host, k)
            logger.debug("Binding to %s" % str(sock.getsockname()))
            self.localaddr = sock.getsockname()
        else:
            sock = common.sock_open(self.host, k, localaddr=self.localaddr)
        return sock

    def get_knocks(self):
        return self.knocks
