pk: A Port Knocking server daemon and client
===

#Introduction
`pk` is a way to expose services behind a layer that employs a port-knocking protocol to control client access. The client and server applications use a simple shared secret to negotiate access. 

The daemon installs an `iptables` rule to DROP all TCP traffic to the provided service port, removing the filter on a successful knock.

##Server

```python

from pk import server

secret_port = 8080
secret = "very-secret"

# setup portknocker daemon
daemon = server.PkDaemon()
daemon.register(secret_port, secret)
daemon.start()
```

##Client

```python

from pk import client

secret = "very-secret"
pkclient = client.PkClient(host, secret)

# Get a socket connection to the hidden service
hidden_conn = pkclient.connect()
```

##TODO
Cool enhancements:

 - Support for multiple hidden services
 - Support for closing the firewall after timeout using heartbeat from client socket
 - Support for timing out multiple clients to the same service
