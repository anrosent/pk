import logging

logger = logging.getLogger(__name__)

class KnockMuxer:

    client_state = {}

    def __init__(self, knock, sockmap):
        self.knock = knock
        self.sockmap = sockmap

    def put(self, sock, client):
        logger.debug("Knock on %s from client %s" % (str(sock.getsockname()), str(client)))
        if client in self.client_state:
            logger.debug("Found state for client %s" % str(client))
            state = self.client_state[client]
        else:
            state = KnockState(self.knock, self.sockmap)
            self.client_state[client] = state
        return state.put(sock)

    def get_sockmap(self):
        return self.sockmap

class KnockState:
    
    def __init__(self, knock, sockmap):
        self.knock = knock
        self.sockmap = sockmap
        self._ix = 0

    def put(self, sock):
        k = self.sockmap[sock]
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
