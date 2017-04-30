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
#%% socket message types
###


class SocketMessageType(abc.ABC):
    """
    Base class providing `send()` and `recv()` methods for sending and
    receiving (higher-level) messages via the socket `socket`.
    """

    @abc.abstractmethod
    def send(self, socket, x):
        pass

    @abc.abstractmethod
    def recv(self, socket):
        pass


class ByteSocketMessageType(SocketMessageType):
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

    def __init__(self, compress=False):
        self._compress = compress

    def _recvn(self, socket, byteCount):
        """
        Receive and return a fixed number of `byteCount` bytes from the socket.
        """
        b = io.BytesIO()
        while True:
            currentByteCount = b.getbuffer().nbytes
            if currentByteCount >= byteCount:
                break
            packet = socket.recv(byteCount - currentByteCount)
            if len(packet) == 0:
                return None
            b.write(packet)
        return b.getvalue()

    def send(self, socket, b):
        if self._compress:
            b = zlib.compress(b)
        header = struct.pack(">I", int(len(b)))
        socket.sendall(header + b)

    def recv(self, socket):
        header = self._recvn(4)
        if header is None:
            return None
        length = struct.unpack(">I", header)[0]
        b = self._recvn(socket, length)
        if self._compress:
            b = zlib.decompress(b)
        return b


class NumpySocketMessageType(ByteSocketMessageType):
    """
    Class providing `send()` and `recv()` methods for sending and receiving
    NumPy ndarray objects via the given socket.
    """

    def __init__(self, *args, **kwargs):
        if _NUMPY_ERROR is not None:
            raise _NUMPY_ERROR
        super().__init__(*args, **kwargs)

    def send(self, socket, x):
        b = io.BytesIO()
        np.save(file=b, arr=x, allow_pickle=False, fix_imports=False)
        super().send(socket, b.getvalue())

    def recv(self, socket):
        b = io.BytesIO(super().recv(socket))
        return np.load(file=b, allow_pickle=False, fix_imports=False)


class JsonSocketMessageType(ByteSocketMessageType):
    """
    Class providing `send()` and `recv()` methods for sending and receiving
    JSON-serializable objects via the given socket.
    """

    def send(self, socket, x):
        j = json.dumps(x, ensure_ascii=True)
        b = bytes(j, "ascii")
        super().send(socket, b)

    def recv(self, socket):
        b = super().recv(socket)
        j = b.decode("ascii")
        x = json.loads(j)
        return x


class ExtendedJsonSocketMessageType(ByteSocketMessageType):
    """
    Class providing `send()` and `recv()` methods for sending and receiving
    JSON-serializable (with extended range of supported types, see
    `dh.utils.ejson`) objects via the given socket.

    .. see:: `dh.utils.ejson`.
    """

    def send(self, socket, x):
        j = dh.utils.ejson.dumps(x)
        b = bytes(j, "ascii")
        super().send(socket, b)

    def recv(self, socket):
        b = super().recv(socket)
        j = b.decode("ascii")
        x = dh.utils.ejson.loads(j)
        return x


###
#%% extended socket with support for multiple message types
###


class MessageSocket(socket.socket):
    """
    This is a socket which supports the methods `msend()` and `mrecv()`, which
    send/receive entire (higher-level) messages.

    For both methods, the `messageType` argument must be an instance of the
    class `SocketMessageType`.

    Note: in this context, 'message' means a high-level, user-defined object,
    not the 'message' used in the context of `socket.socket.recvmsg` and
    `socket.socket.sendmsg`.
    """

    def msend(self, messageType, x):
        messageType.send(self, x)

    def mrecv(self, messageType):
        messageType.recv(self)


###
#%% socket servers/clients
###


class SocketServer(abc.ABC):
    """
    Simple socket server which accepts connections on the specified `host`
    and `port` and communicates using the specified message type `messageClass`
    in the method `handler`.

    See http://stackoverflow.com/a/19742674/1913780 for an explanation of
    `nodelay`.
    """

    def __init__(self, host="", port=7214, backlog=5, nodelay=True):
        print("Creating socket...")
        self._socket = MessageSocket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if nodelay:
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        print("Binding socket to {}:{}...".format(host if len(host) > 0 else "*", port))
        self._socket.bind((host, port))
        self._backlog = backlog
        self._nodelay = nodelay

    def _print(self, text):
        print("[{}]  {}".format(dh.utils.dtstr(compact=False), text))

    @property
    def socket(self):
        return self._socket

    def run(self):
        self._socket.listen(self._backlog)
        while True:
            self._print("Waiting for connection...")
            sys.stdout.flush()
            (connectionSocket, connectionAddress) = self._socket.accept()
            self._print("Accepted connection from {}:{}".format(connectionAddress[0], connectionAddress[1]))
            t0 = time.time()
            try:
                self.communicate()
            except Exception as e:
                self._print("** {}: {}".format(type(e).__name__, e))
            self._print("Finished request from {}:{} after {} ms".format(connectionAddress[0], connectionAddress[1], dh.utils.around((time.time() - t0) * 1000.0)))

    @abc.abstractmethod
    def communicate(self):
        """
        Implements the entire communication happening for one connection with a
        client via high-level socket messages (see `SocketMessageType`).

        Counterpart of `SocketClient.communicate`. See specific client/server
        implementations for examples.
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

    def __init__(self, host, port=7214, nodelay=True):
        self._host = host
        self._port = port
        self._nodelay = nodelay

    @property
    def socket(self):
        return self._socket

    def query(self, *args, **kwargs):
        # establish connection with the server
        self._socket = MessageSocket(socket.AF_INET, socket.SOCK_STREAM)
        if self._nodelay:
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self._socket.connect((self._host, self._port))

        # user-specific communication
        res = self.communicate(*args, **kwargs)

        # close connection
        self._socket.shutdown(socket.SHUT_RDWR)
        self._socket.close()

        return res

    @abc.abstractmethod
    def communicate(self, *args, **kwargs):
        """
        Implements the entire communication happening for one connection with a
        server via high-level socket messages (see `SocketMessageType`).

        Counterpart of `SocketServer.communicate`. See specific client/server
        implementations for examples.
        """
        pass


class ImageProcessingServer(SocketServer):
    """
    Special case of `SocketServer` which accepts a NumPy array and JSON-encoded
    parameters and returns a NumPy array. The counterpart is the
    `ImageProcessingClient` class.

    To specify the processing behavior, sub-class this class and implement
    the static method `process(data, params)`.
    """

    def communicate(self):
        # receive input image and parameters
        data = self.socket.mrecv(NumpySocketMessageType())
        params = self.socket.mrecv(JsonSocketMessageType())

        # process and send result image
        try:
            result = self.process(data=data, params=params)
        except Exception as e:
            self._print("** {}: {}".format(type(e).__name__, e))
            result = np.zeros(shape=(0, 0), dtype="uint8")
        else:
            self.socket.msend(NumpySocketMessageType(), result)

    @staticmethod
    @abc.abstractmethod
    def process(data, params):
        """
        This function specifies the processing behavior of this server and must
        be implemeted by the user.
        """
        pass


class ImageProcessingClient(SocketClient):
    """
    Special case of `SocketClient` which sends a NumPy array and JSON-encoded
    parameters and receives a NumPy array. The counterpart is the
    `ImageProcessingServer` class.

    The processing behavior is specified by sub-classing
    `ImageProcessingServer` and implementing the static method
    `process(data, params)`.
    """

    def communicate(self, data, params):
        # send input image and parameters
        self.socket.msend(NumpySocketMessageType(), data)
        self.socket.msend(JsonSocketMessageType(), params)

        # reveive result image
        return self.socket.mrecv(NumpySocketMessageType())

    def process(self, data, params):
        """
        Just another name for the `query` method.
        """
        return self.query(data=data, params=params)
