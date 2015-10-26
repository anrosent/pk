pk: A Port Knocking server daemon and client
===

#Introduction
`pk` is a way to expose services behind a layer that employs a port-knocking protocol to control client access. The client and server applications use a shared secret, a tuple `(host, port_range, secret, knock length)` to negotiate access. 

Currently the hidden service is expected to be running on a network socket, which defeats the purpose of the `pk` daemon somewhat, since someone portscanning would just find the hidden service anyway. I think the next step is to keep the daemon involved as a gateway to the hidden service, which is only serving on loopback or a UNIX socket, instead of providing the client direct socket access.

#What this looks like 

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

secret_port = 8080
secret = "very-secret"
pkclient = client.PkClient(secret_host, secret)

# Get a socket connection to the hidden service
hidden_conn = pkclient.connect()
```
