"""
Tools for network communication.
"""

import abc
import io
import json
import socket
import struct
import sys
import time
import zlib

import dh.utils

import dh.data
import dh.image

# NumPy is only needed for some parts and is optional
try:
    import numpy as np
except ImportError as e:
    _NUMPY_ERROR = e
else:
    _NUMPY_ERROR = None


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

    If `compress` is `True`, messages are compressed before sending and
    decompressed after receiving. This reduces the network load but costs more
    time. The value for `compress` must be the same for both the server and the
    client.
    """

    def __init__(self, socket, compress=False):
        super().__init__(socket=socket)
        self._compress = compress

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
        if self._compress:
            b = zlib.compress(b)
        header = struct.pack(">I", int(len(b)))
        self.socket.sendall(header + b)

    def recv(self):
        header = self._recvn(4)
        if header is None:
            return None
        length = struct.unpack(">I", header)[0]
        b = self._recvn(length)
        if self._compress:
            b = zlib.decompress(b)
        return b


class NumpySocketMessage(ByteSocketMessage):
    """
    Class providing `send()` and `recv()` methods for sending and receiving
    NumPy ndarray objects via the given socket.
    """

    def __init__(self, *args, **kwargs):
        if _NUMPY_ERROR is not None:
            raise _NUMPY_ERROR
        super().__init__(*args, **kwargs)

    def send(self, x):
        b = io.BytesIO()
        np.save(file=b, arr=x, allow_pickle=False, fix_imports=False)
        super().send(b.getvalue())

    def recv(self):
        b = io.BytesIO(super().recv())
        return np.load(file=b, allow_pickle=False, fix_imports=False)


class JsonSocketMessage(ByteSocketMessage):
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


class ExtendedJsonSocketMessage(ByteSocketMessage):
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

    See http://stackoverflow.com/a/19742674/1913780 for an explanation of
    `nodelay`.
    """

    def __init__(self, host="", port=7214, backlog=5, nodelay=True, messageClass=ByteSocketMessage):
        print("Creating socket...")
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if nodelay:
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        print("Binding socket to {}:{}...".format(host if len(host) > 0 else "*", port))
        self._socket.bind((host, port))
        self._backlog = backlog
        self._nodelay = nodelay
        self._messageClass = messageClass

    def _print(self, text):
        print("[{}]  {}".format(dh.utils.dtstr(compact=False), text))

    def run(self):
        self._socket.listen(self._backlog)
        while True:
            self._print("Waiting for connection...")
            sys.stdout.flush()
            (connectionSocket, connectionAddress) = self._socket.accept()
            self._print("Accepted connection from {}:{}".format(connectionAddress[0], connectionAddress[1]))
            t0 = time.time()
            communication = self._messageClass(connectionSocket)
            try:
                self.handler(communication=communication)
            except Exception as e:
                self._print("** {}: {}".format(type(e).__name__, e))
            self._print("Finished request from {}:{} after {} ms".format(connectionAddress[0], connectionAddress[1], dh.utils.around((time.time() - t0) * 1000.0)))

    @abc.abstractmethod
    def handler(self, communication):
        """
        In here, `communication.send()` and `communication.recv()` can be used
        (see `SocketMessage`).
        """
        pass


class SocketClient(abc.ABC):
    """
    Simple socket client which connects to the server on the specified `host`
    and `port` each time `query()` is called. It communicates using the
    specified message type `messageClass` in the method `handler`.

    See http://stackoverflow.com/a/19742674/1913780 for an explanation of
    `nodelay`.
    """

    def __init__(self, host, port=7214, nodelay=True, messageClass=ByteSocketMessage):
        self._host = host
        self._port = port
        self._nodelay = nodelay
        self._messageClass = messageClass

    def query(self, *args, **kwargs):
        # establish connection with the server
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self._nodelay:
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
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

    def __init__(self, *args, **kwargs):
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
        return res["result"]


class ImageProcessingServer(SocketServer):
    """
    Special case of `SocketServer` which accepts a NumPy array and JSON-encoded
    parameters and returns a NumPy array. The counterpart is the
    `ImageProcessingClient` class.

    To specify the processing behavior, sub-class this class and implement
    the static method `process(data, params)`.

    In contrast to `DataProcessingServer`, this class is less flexible but has
    a lower response latency.
    """

    def __init__(self, *args, **kwargs):
        kwargs["messageClass"] = NumpySocketMessage
        super().__init__(*args, **kwargs)

    def handler(self, communication):
        data = communication.recv()
        params = JsonSocketMessage(communication.socket).recv()
        try:
            result = self.process(data=data, params=params)
        except Exception as e:
            self._print("** {}: {}".format(type(e).__name__, e))
            communication.send(np.zeros(shape=(0, 0), dtype="uint8"))
        else:
            communication.send(result)

    @staticmethod
    @abc.abstractmethod
    def process(data, params):
        pass


class ImageProcessingClient(SocketClient):
    """
    Special case of `SocketClient` which sends a NumPy array and JSON-encoded
    parameters and receives a NumPy array. The counterpart is the
    `ImageProcessingServer` class.

    The processing behavior is specified by sub-classing
    `ImageProcessingServer` and implementing the static method
    `process(data, params)`.

    In contrast to `DataProcessingClient`, this class is less flexible but has
    a lower response latency.
    """

    def __init__(self, *args, **kwargs):
        kwargs["messageClass"] = NumpySocketMessage
        super().__init__(*args, **kwargs)

    def process(self, data, params):
        return self.query(data=data, params=params)

    def handler(self, data, params, communication):
        communication.send(data)
        JsonSocketMessage(communication.socket).send(params)
        res = communication.recv()
        return res
