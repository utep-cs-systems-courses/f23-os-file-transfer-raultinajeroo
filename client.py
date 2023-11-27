#! /usr/bin/env python3

# Echo client program
import re
import socket
import sys

sys.path.append("lib")  # for params
import params

sys.path.append("archiver")  # for archiver
import archiver as arc

switchesVarDefaults = (
    (("-s", "--server"), "server", "127.0.0.1:50001"),
    (("-?", "--usage"), "usage", False),  # boolean (set if present)
)

# progname = "client"  -  Not needed
paramMap = params.parseParams(switchesVarDefaults)

server, usage = paramMap["server"], paramMap["usage"]

if usage:
    params.usage()

try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print(f"Can't parse server:port from '{server}'")
    sys.exit(1)


def open_sock():
    server = None
    for res in socket.getaddrinfo(
        serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM
    ):
        af, socktype, proto, canonname, sa = res
        try:
            print(f"Creating sock: af={af}, type={socktype}, proto={proto}")
            server = socket.socket(af, socktype, proto)
        except socket.error as msg:
            print(f" error: {msg}")
            server = None
            continue
        try:
            print(f" attempting to connect to {repr(sa)}")
            server.connect(sa)
        except socket.error as msg:
            print(f" error: {msg}")
            server.close()
            server = None
            continue
        break

    if server is None:
        print("could not open socket")
        sys.exit(1)
    return server


def get_paths(choice):
    paths = input(f"File(s) to be {choice} (comma separated): ")
    paths = paths.replace(" ", "").split(",")
    return paths


def client_interaction(server):
    while True:
        print("-------------------------------\n")
        print("What would you like to do?")
        print("1. Transfer file(s)")
        print("2. Request file(s)")
        print("3. Exit")
        choice = input("> ")

        if choice == "3":
            print("Exiting file transfer. Goodbye!")
            server.close()
            break
        elif choice not in ["1", "2"]:
            print("Invalid choice, please try again.")
            continue

        if choice == "1":  # Transfer
            try:
                for path in get_paths("transferred"):
                    arc.transfer(server, path)
            except socket.error:
                print("Error transferring file(s).")
                sys.exit(1)
        elif choice == "2":  # Request
            try:
                for path in get_paths("requested"):
                    arc.request(server, path, tag="req")
            except socket.error:
                print("Error requesting file(s).")
                sys.exit(1)


def __main__():
    server = open_sock()
    client_interaction(server)


if __name__ == "__main__":
    __main__()
