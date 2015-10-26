from pk import client

def testPkConnect():
    c = client.PortKock("localhost", "secret")
    ports = c.get_knock()

    common.on_thread(c.connect)
