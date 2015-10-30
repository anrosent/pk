#!/usr/bin/env python3
import argparse
import sys
from pk import client

def run(args):
    c = client.PkClient(args.host, args.secret)
    sock = c.connect()
    while True:
        line = sys.stdin.readline()
        sock.sendall(line.encode('utf8'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="remote server we're contacting")
    parser.add_argument("secret", help="PK secret")

    args = parser.parse_args()
    run(args)
