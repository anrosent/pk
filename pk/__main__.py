from sys import argv

from pk import server

if argv[1] == 'server':
    server = server.PkDaemon()
    secret = "secret"

    server.register(8080, secret)
    server.start()

