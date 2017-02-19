"""
Tools for network communication.
"""

import abc
import io
import json
import socket
import struct
import sys
import zlib

import dh.utils

import dh.data
import dh.image


###
#%% sockets
###


class SocketMessage(abc.ABC):
    """
    Base class providing `send()` and `recv()` methods for sending and
    receiving (higher-level) messages via the specified socket `socket`.
    """

    def __init__(self, socket):
        self._socket = socket

    @property
    def socket(self):
        return self._socket

    @abc.abstractmethod
    def send(self, x):
        pass

    @abc.abstractmethod
    def recv(self):
        pass


class ByteSocketMessage(SocketMessage):
    """
    Class providing methods for sending and receiving byte *messages* of up to
    4 GiB in size via a given socket.

    Each message has a fixed-length (four byte) header, specifying the length
    of the message content. Thus, calls to `send()` and `recv()` always
    ensure that the entire message is being sent/received.
    """

    def _recvn(self, byteCount):
        """
        Receive and return a fixed number of `byteCount` bytes from the socket.
        """
        b = io.BytesIO()
        while True:
            currentByteCount = b.getbuffer().nbytes
            if currentByteCount >= byteCount:
                break
            packet = self.socket.recv(byteCount - currentByteCount)
            if len(packet) == 0:
                return None
            b.write(packet)
        return b.getvalue()

    def send(self, b):
        header = struct.pack(">I", int(len(b)))
        self.socket.sendall(header + b)

    def recv(self):
        header = self._recvn(4)
        if header is None:
            return None
        size = struct.unpack(">I", header)[0]
        return self._recvn(size)


class GzipByteSocketMessage(ByteSocketMessage):
    """
    Class providing `send()` and `recv()` methods for sending and receiving
    byte messages via the given socket. In contrast to `ByteSocketMessage`, the
    byte messages are gzipped before being sent and unzipped after being
    received.
    """

    def send(self, b):
        z = zlib.compress(b)
        super().send(z)

    def recv(self):
        z = super().recv()
        b = zlib.decompress(z)
        return b


class JsonSocketMessage(GzipByteSocketMessage):
    """
    Class providing `send()` and `recv()` methods for sending and receiving
    JSON-serializable objects via the given socket.
    """

    def send(self, x):
        j = json.dumps(x, ensure_ascii=True)
        b = bytes(j, "ascii")
        super().send(b)

    def recv(self):
        b = super().recv()
        j = b.decode("ascii")
        x = json.loads(j)
        return x


class ExtendedJsonSocketMessage(GzipByteSocketMessage):
    """
    Class providing `send()` and `recv()` methods for sending and receiving
    JSON-serializable (with extended range of supported types, see
    `dh.utils.ejson`) objects via the given socket.

    .. see:: `dh.utils.ejson`.
    """

    def send(self, x):
        j = dh.utils.ejson.dumps(x)
        b = bytes(j, "ascii")
        super().send(b)

    def recv(self):
        b = super().recv()
        j = b.decode("ascii")
        x = dh.utils.ejson.loads(j)
        return x


class SocketServer(abc.ABC):
    """
    Simple socket server which accepts connections on the specified `host`
    and `port` and communicates using the specified message type `messageClass`
    in the method `handler`.
    """

    def __init__(self, host=None, port=7214, backlog=5, messageClass=ByteSocketMessage):
        print("Creating socket...")
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Binding socket to {}:{}...".format(host, port))
        self._socket.bind((host, port))
        self._backlog = backlog
        self._messageClass = messageClass

    def run(self):
        self._socket.listen(self._backlog)
        while True:
            print("Waiting for connection...")
            sys.stdout.flush()
            (connectionSocket, connectionAddress) = self._socket.accept()
            print("Accepted connection from {}:{}".format(connectionAddress[0], connectionAddress[1]))
            communication = self._messageClass(connectionSocket)
            self.handler(communication=communication)

    @abc.abstractmethod
    def handler(self, communication):
        pass


class SocketClient(abc.ABC):
    """
    Simple socket client which connects to the server on the specified `host`
    and `port` each time `query()` is called. It communicates using the
    specified message type `messageClass` in the method `handler`.
    """

    def __init__(self, host, port=7214, messageClass=ByteSocketMessage):
        self._host = host
        self._port = port
        self._messageClass = messageClass

    def query(self, *args, **kwargs):
        # establish connection with the server
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self._host, self._port))

        # user-specific communication
        communication = self._messageClass(self._socket)
        res = self.handler(*args, communication=communication, **kwargs)

        # close connection
        self._socket.shutdown(socket.SHUT_RDWR)
        self._socket.close()

        return res

    @abc.abstractmethod
    def handler(self, *args, communication, **kwargs):
        """
        In here, `communication.send()` and `communication.recv()` can be used
        (see `SocketMessage`).
        """
        pass


class DataProcessingServer(SocketServer):
    """
    Special case of `SocketServer` which accepts dictionary messages having the
    keys `"data"` and `"params"` and returns a dictionary with keys `"status"`
    and `"result"`. The counterpart is the `DataProcessingClient` class.

    To specify the processing behavior, sub-class this class and implement
    the static method `process(data, params)`.
    """

    def __init__(self, fun, *args, **kwargs):
        kwargs["messageClass"] = ExtendedJsonSocketMessage
        super().__init__(*args, **kwargs)

    def handler(self, communication):
        x = communication.recv()
        try:
            (data, params) = (x["data"], x["params"])
            result = self.process(data=data, params=params)
        except Exception as e:
            communication.send({"status": "ERROR ({}: {})".format(type(e).__name__, e), "result": None})
        else:
            communication.send({"status": "OK", "result": result})

    @staticmethod
    @abc.abstractmethod
    def process(data, params):
        pass


class DataProcessingClient(SocketClient):
    """
    Special case of `SocketClient` which sends dictionary messages having the
    keys `"data"` and `"params"` and receives a dictionary with keys `"status"`
    and `"result"`. The counterpart is the `DataProcessingServer` class.

    The processing behavior is specified by sub-classing `DataProcessingServer`
    and implementing the static method `process(data, params)`.
    """

    def __init__(self, *args, **kwargs):
        kwargs["messageClass"] = ExtendedJsonSocketMessage
        super().__init__(*args, **kwargs)

    def process(self, data, params):
        return self.query(data=data, params=params)

    def handler(self, data, params, communication):
        communication.send({"data": data, "params": params})
        res = communication.recv()
        if res["status"] != "OK":
            raise RuntimeError("Received non-OK result status: ''".format(res["status"]))
        return res
