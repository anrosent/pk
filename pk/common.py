import hashlib
import threading
import socket

NUM_KNOCKS = 10

def mhash(s):
    return int.from_bytes(hashlib.md5(s.encode('utf8')).digest(), 'little')

def make_int(s):
    return int.from_bytes(s.encode('utf8'), 'little')

def _make_knocks(secret, prange):
    return [_make_knock(secret, i, prange) for i in range(NUM_KNOCKS)]

def _make_knock(secret, knock_ix, prange):
    rsize = prange[-1] - prange[0]
    return (mhash(secret + str(knock_ix)) % rsize) + prange[0]

def sock_open(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # TODO: timeout
    sock.connect((host, port))
    return sock 

def on_thread(f, *args, **kwargs):
    t = threading.Thread(target=f, args=args, kwargs=kwargs)
    t.start()
    return t
