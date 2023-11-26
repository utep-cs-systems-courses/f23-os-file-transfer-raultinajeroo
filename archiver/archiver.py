#!/usr/bin/env python3
import os
import socket
import sys

delimiter = "\n"


def transfer(server, path, client=True):
    def framer(path, file_size, file_content):
        # Frame and write file information and content
        server.send(f"{path}{delimiter}".encode())
        server.send(f"{file_size}{delimiter}".encode())
        server.sendall(file_content)
        print(f"Sending {path} ({file_size} bytes)")

    if os.path.isfile(path):
        if client:
            spaces = " " * (512 - len(path) - len("transfer"))
            server.send(f"transfer{spaces}{path}".encode())

        with open(path, "rb") as f:
            file_size = os.fstat(f.fileno()).st_size
            file_content = f.read()
            framer(path, file_size, file_content)
    else:
        if not client:
            server.send(f"<N/A>{delimiter}".encode())
        print(f"Error: {path} is not a file")


def request(server, path, client=True, tag=""):
    def unframer():
        # Read framed data from stdin
        file_name = read_until_delimiter(server)
        if file_name == "<N/A>":
            print(f"Error: {path} is not a file")
            return

        file_size = int(read_until_delimiter(server))
        file_bytes = server.recv(file_size)
        print(f"Receiving {path} ({file_size} bytes)")
        with open(str(tag) + "_" + path, "wb") as f:
            f.write(file_bytes)

    if client:
        spaces = " " * (512 - len(path) - len("transfer"))
        server.send(f"request{spaces}{path}".encode())
    unframer()


def read_until_delimiter(sock):
    enc_delimiter = delimiter.encode()
    data = b""
    n = len(delimiter)
    while True:
        data += sock.recv(1)
        if data[-n:] == enc_delimiter:
            break
    return data[:-n].decode()
