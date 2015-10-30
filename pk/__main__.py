import argparse
from sys import argv

from pk import server

parser = argparse.ArgumentParser("pk")
parser.add_argument("p", metavar="service_port", type=int, help="the port we're hiding")
parser.add_argument("secret", help="shared secret for knocking")
parser.add_argument("mode", choices=["server"], help="stub in case there's a client mode?")

args = parser.parse_args()

if args.mode == "server":
    server = server.PkDaemon()
    server.register(args.p, args.secret)
    server.start()

