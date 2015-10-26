import socket
from pk import client, server, common

def testPkConnect():

    # Setup secret service
    secret_host = "127.0.0.1"
    secret_port = 8080
    secret = "secret"

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', secret_port))
    common.on_thread(sock.listen, 1)

    # setup portknocker daemon
    s = server.PortKnockerManager()
    s.register(secret_port, secret)
    common.on_thread(s.start)
    
    # use PK client to connect
    c = client.PortKnockClient(secret_host, secret)
    conn = c.connect()

    # Verify that we got redirect to the secret host
    print(conn.getpeername())
    assert conn.getpeername() == (secret_host, secret_port)

    # Kill server gracefully
    s.stop()
