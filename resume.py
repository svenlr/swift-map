#!/usr/bin/env python3

import socket
import time

time.sleep(5)
s = socket.socket()
s.connect(("localhost", 24679))
s.close()
