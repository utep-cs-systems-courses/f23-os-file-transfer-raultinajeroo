#! /usr/bin/env python3

# Echo server program

import os
import random as rand  # Select Timeout
import re
import select
import socket
import sys

sys.path.append("lib")  # for params
import params

sys.path.append("archiver")  # for archiver
import archiver as arc

switchesVarDefaults = (
    (("-l", "--listenPort"), "listenPort", 50001),
    (("-?", "--usage"), "usage", False),  # boolean (set if present)
)

# progname = "server"  -  Not needed
paramMap = params.parseParams(switchesVarDefaults)
listenPort, usage = paramMap["listenPort"], paramMap["usage"]

if usage:
    params.usage()

listenPort = paramMap["listenPort"]
listenAddr = ""  # Symbolic name meaning all available interfaces


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((listenAddr, listenPort))
    server.listen()

    input = [server]

    try:
        while True:
            readable, writable, _ = select.select(input, [], [], rand.random())
            for sock in readable:
                if sock is server:
                    # Accept new connection
                    print("New connection established.")
                    client, address = server.accept()
                    input.append(client)
                else:
                    action, path = sock.recv(512).decode().split()
                    if action == "transfer":
                        arc.request(sock, path, client=False, tag="tra")
                    elif action == "request":
                        arc.transfer(sock, path, client=False)
                    elif action == "":
                        # Close the connection if client sends an empty message
                        print("Closing connection with a client")
                        input.remove(sock)
                        sock.close()
    except KeyboardInterrupt:
        print("Closing server...")
        for sock in input:
            sock.close()
        server.close()
