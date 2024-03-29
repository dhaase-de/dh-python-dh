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

import dh.ejson
import dh.log
import dh.utils

# NumPy is only needed for some parts and is optional
try:
    import numpy as np
except ImportError as e:
    _NUMPY_ERROR = e
else:
    _NUMPY_ERROR = None


###
#%% exceptions
###


class InvalidMessageHeaderError(Exception): pass
class InvalidMessageBodyError(Exception): pass


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


class RawByteSocketMessageType(SocketMessageType):
    """
    Class providing methods for sending and receiving raw bytes (not messages) via a given socket.
    """

    def __init__(self, maxByteCount=None):
        self.maxByteCount = maxByteCount

    @staticmethod
    def _recvn(socket, byteCount=None):
        """
        Receive and return a fixed number of `byteCount` bytes from the socket.
        """
        b = io.BytesIO()
        while True:
            if byteCount is not None:
                # there is a max byte count we want to receive
                currentByteCount = b.getbuffer().nbytes
                if currentByteCount >= byteCount:
                    break
                packet = socket.recv(byteCount - currentByteCount)
            else:
                # there is NO max byte count we want to receive
                packet = socket.recv(1024)

            if len(packet) > 0:
                b.write(packet)
            else:
                break

        if byteCount is not None:
            return b.getvalue()[:byteCount]
        else:
            return b.getvalue()

    def send(self, socket, b):
        socket.sendall(b)

    def recv(self, socket):
        return self._recvn(socket, byteCount=self.maxByteCount)


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

    def send(self, socket, b):
        if self._compress:
            b = zlib.compress(b)
        header = struct.pack(">I", int(len(b)))
        socket.sendall(header + b)

    def recv(self, socket):
        # receive header which specifies the length of the message (in bytes)
        header = RawByteSocketMessageType._recvn(socket, 4)
        if len(header) != 4:
            raise InvalidMessageHeaderError("Received invalid header ({})".format(header))
        length = struct.unpack(">I", header)[0]

        # receive actual message
        b = RawByteSocketMessageType._recvn(socket, length)
        if len(b) != length:
            raise InvalidMessageBodyError("Received message body of {} byte(s), but header specified {} byte(s)".format(len(b), length))

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
    `dh.ejson`) objects via the given socket.

    .. seealso:: `dh.ejson`.
    """

    def send(self, socket, x):
        j = dh.ejson.dumps(x)
        b = bytes(j, "ascii")
        super().send(socket, b)

    def recv(self, socket):
        b = super().recv(socket)
        j = b.decode("ascii")
        x = dh.ejson.loads(j)
        return x


###
#%% extended socket with support for multiple message types
###


class MessageSocket():
    """
    This is a wrapper class for `socket.socket` which supports the methods
    `msend()` and `mrecv()`, which send/receive entire (higher-level) messages.

    For both methods, the `messageType` argument must be an instance of the
    class `SocketMessageType`.

    Note: in this context, 'message' means a high-level, user-defined object,
    not the 'message' used in the context of `socket.socket.recvmsg` and
    `socket.socket.sendmsg`.
    """

    def __init__(self, socket):
        self._socket = socket

    def msend(self, messageType, x):
        messageType.send(self._socket, x)

    def mrecv(self, messageType):
        return messageType.recv(self._socket)


###
#%% socket servers/clients
###


class ServerLoggerFormatter(dh.log.LongLoggerFormatter):
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port

    def getPreAndPostfixes(self, level, timestamp, **kwargs):
        (pre1, pre2, post1, post2) = super().getPreAndPostfixes(level=level, timestamp=timestamp, **kwargs)
        customPre = "[{}:{}]  ".format(self.host, self.port)
        return (customPre + pre1, " " * len(customPre) + pre2, post1, post2)


class SocketServer(abc.ABC):
    """
    Simple socket server which accepts connections on the specified `host`
    and `port` and communicates with the client as specified in
    `communicate()`.

    See http://stackoverflow.com/a/19742674/1913780 for an explanation of
    `nodelay`.
    """

    def __init__(self, host="", port=7214, backlog=5, nodelay=True, logger=None):
        hostStr = host if len(host) > 0 else "*"

        # set up logger
        self.logger = logger
        if self.logger is None:
            self.logger = dh.log.Logger(ServerLoggerFormatter(host=hostStr, port=port))

        self.logger.info("Creating socket...")
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if nodelay:
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        self.logger.info("Binding socket to {}:{}...".format(hostStr, port))
        self._socket.bind((host, port))
        self._backlog = backlog
        self._nodelay = nodelay
        
        self.requestCount = 0

    def run(self):
        self._socket.listen(self._backlog)
        while True:
            self.logger.info("Waiting for connection...")
            sys.stdout.flush()
            (connectionSocket, connectionAddress) = self._socket.accept()
            self.requestCount += 1
            self.logger.info("[request #{}]  Accepted connection from {}:{}".format(self.requestCount, connectionAddress[0], connectionAddress[1]))
            t0 = time.time()
            try:
                self.communicate(MessageSocket(connectionSocket))
            except Exception as e:
                self.logger.error("[request #{}]  {}: {}".format(self.requestCount, type(e).__name__, e))
            else:
                self.logger.success("[request #{}]  Finished request from {}:{} after {} ms".format(self.requestCount, connectionAddress[0], connectionAddress[1], dh.utils.around((time.time() - t0) * 1000.0)))
            finally:
                connectionSocket.close()

    @abc.abstractmethod
    def communicate(self, socket):
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
    and `port` each time `query()` is called. The communication with the server
    is specified in `communicate()`.

    See http://stackoverflow.com/a/19742674/1913780 for an explanation of
    `nodelay`.
    """

    def __init__(self, host, port=7214, nodelay=True):
        self._host = host
        self._port = port
        self._nodelay = nodelay

    def query(self, *args, **kwargs):
        # establish connection with the server
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self._nodelay:
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self._socket.connect((self._host, self._port))

        # actual communication, keep result
        result = self.communicate(MessageSocket(self._socket), *args, **kwargs)

        # close connection
        self._socket.shutdown(socket.SHUT_RDWR)
        self._socket.close()

        return result

    @abc.abstractmethod
    def communicate(self, socket, *args, **kwargs):
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

    def communicate(self, socket):
        # receive input image and parameters
        data = socket.mrecv(NumpySocketMessageType())
        params = socket.mrecv(JsonSocketMessageType())

        # process
        try:
            result = self.process(data=data, params=params)
        except Exception as e:
            self.logger.error("[request #{}]  {}: {}".format(self.requestCount, type(e).__name__, e))
            result = np.zeros(shape=(0, 0), dtype="uint8")

        # send result image
        socket.msend(NumpySocketMessageType(), result)

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

    def communicate(self, socket, data, params):
        # send input image and parameters
        socket.msend(NumpySocketMessageType(), data)
        socket.msend(JsonSocketMessageType(), params)

        # receive result image
        return socket.mrecv(NumpySocketMessageType())

    def process(self, data, params):
        """
        Just another name for the `query` method (to better show the connection
        to the server's `process` method).
        """
        return self.query(data=data, params=params)


class ImageProcessingServer2(SocketServer):
    """
    Special case of `SocketServer` which accepts a NumPy array and JSON-encoded
    parameters and returns a NumPy array plus a JSON-encodable object. The
    counterpart is the `ImageProcessingClient2` class.

    To specify the processing behavior, sub-class this class and implement
    the static method `process(data, params)`.
    """

    def communicate(self, socket):
        data = socket.mrecv(NumpySocketMessageType())
        params = socket.mrecv(JsonSocketMessageType())

        # process
        try:
            (result, info) = self.process(data=data, params=params)
        except Exception as e:
            self.logger.error("[request #{}]  {}: {}".format(self.requestCount, type(e).__name__, e))
            result = np.zeros(shape=(0, 0), dtype="uint8")
            info = None

        # send result image and info
        socket.msend(NumpySocketMessageType(), result)
        socket.msend(JsonSocketMessageType(), info)

    @staticmethod
    @abc.abstractmethod
    def process(data, params):
        """
        This function specifies the processing behavior of this server and must
        be implemented by the user.
        """
        pass


class ImageProcessingClient2(SocketClient):
    """
    Special case of `SocketClient` which sends a NumPy array and JSON-encoded
    parameters and receives a NumPy array and a JSON-encoded object. The
    counterpart is the `ImageProcessingServer2` class.

    The processing behavior is specified by sub-classing
    `ImageProcessingServer` and implementing the static method
    `process(data, params)`.
    """

    def communicate(self, socket, data, params):
        # send input image and parameters
        socket.msend(NumpySocketMessageType(), data)
        socket.msend(JsonSocketMessageType(), params)

        # receive result image
        result = socket.mrecv(NumpySocketMessageType())
        info = socket.mrecv(JsonSocketMessageType())
        return (result, info)

    def process(self, data, params):
        """
        Just another name for the `query` method (to better show the connection
        to the server's `process` method).
        """
        return self.query(data=data, params=params)
