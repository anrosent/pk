import hashlib
import threading
import socket

NUM_KNOCKS = 10

# Nothing is registered in this range
min_port, max_port = PORT_RANGE = (38000, 39000)

def mhash(s):
    return int.from_bytes(hashlib.md5(s.encode('utf8')).digest(), 'little')

def make_int(s):
    return int.from_bytes(s.encode('utf8'), 'little')

def _make_knocks(secret):
    return [_make_knock(secret, i) for i in range(NUM_KNOCKS)]

def _make_knock(secret, knock_ix):
    rsize = max_port - min_port
    return (mhash(secret + str(knock_ix)) % rsize) + min_port

def sock_open(host, port, localaddr=None):
    '''
    Let clients pick local addr to reuse if they want for purpose of 
    firewalling hidden services by client addr
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # TODO: timeout
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if localaddr:
        sock.bind(localaddr)

    sock.connect((host, port))
    return sock 

def on_thread(f, *args, **kwargs):
    t = threading.Thread(target=f, args=args, kwargs=kwargs)
    t.start()
    return t
