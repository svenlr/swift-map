#!/usr/bin/env python3.8

import socket

s = socket.socket()
s.connect(("localhost", 24679))
s.close()
