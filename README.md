pk: A Port Knocking server daemon and client
===

#Introduction
`pk` is a way to expose services behind a layer that employs a shared-secret port-knocking protocol to control client access.

When a client successfully authenticates, the daemon responds with the port on which the hidden service is listening, and installs an `iptables` rule to permit the client to connect to the hidden service.

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
 - Support for closing firewall to clients who don't heartbeat to the daemon
