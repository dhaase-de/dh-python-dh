#!/usr/bin/env python3

import dh.network
import dh.utils


class FaultyClient(dh.network.SocketClient):
    def communicate(self, socket):
        socket.msend(dh.network.RawByteSocketMessageType(), b"1234")


def main():
    client = FaultyClient(host="localhost")
    client.query()


if __name__ == "__main__":
    main()
