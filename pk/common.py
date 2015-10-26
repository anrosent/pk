import hashlib
import threading
import socket

def mhash(s):
    return int.from_bytes(hashlib.md5(s.encode('utf8')).digest(), 'little')

def make_int(s):
    return int.from_bytes(s.encode('utf8'), 'little')

def _make_knocks(secret, n_knocks, prange):
    return [_make_knock(secret, i, prange) for i in range(n_knocks)]

def _make_knock(secret, knock_ix, prange):
    rsize = prange[-1] - prange[0]
    return (mhash(secret + str(knock_ix)) % rsize) + prange[0]

def sock_open(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # TODO: timeout
    sock.connect((host, port))
    return sock 

def on_thread(f, args):
    t = threading.Thread(target=f, args=args)
    t.start()
    return t
