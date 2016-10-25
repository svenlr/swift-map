#!/usr/bin/env python2.7

import socket

s = socket.socket()
s.connect(("localhost", 24679))
s.close()
