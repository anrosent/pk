import logging

logger = logging.getLogger(__name__)

class KnockMuxer:

    client_state = {}

    def __init__(self, knock):
        self.knock = knock

    def put(self, localaddr, client):
        lh, lp = localaddr
        logger.debug("Knock on %s from client %s" % (str(localaddr), str(client)))
        if client in self.client_state:
            logger.debug("Found state for client %s" % str(client))
            state = self.client_state[client]
        else:
            state = KnockState(self.knock)
            self.client_state[client] = state
        correct, done = state.put(lp)
        if not correct:
            del client_state[client]
        return done

class KnockState:
    
    def __init__(self, knock):
        self.knock = knock
        self._ix = 0

    def put(self, port):
        if self.knock[self._ix] != port:
            logger.debug("Wrong knock, deleting")
            return False, False
        elif self._ix == len(self.knock) - 1:
            logger.debug("Correct, sequence complete")
            return True, True
        else:
            self._ix += 1
            logger.debug("Correct, advancing to knock %s/%s" % (self._ix, len(self.knock)))
            return True, False
