# -*- coding: utf-8 -*-
import socket
import json

class ClientNetwork:

    def __init__(self, host='localhost', port=8888, timeout=5.0):
        """
        Initialize the client.

        :param host: Server hostname or IP.
        :param port: Server port.
        :param timeout: Connection timeout in seconds.
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = None

    def connect(self):
        """
        Establish a TCP connection to the configured server.

        :return: None
        """
        if self.sock:
            return
        self.sock = socket.create_connection((self.host, self.port), timeout=self.timeout)

    def close(self):
        """
        Close the socket connection.

        :return: None
        """
        if self.sock:
            try:
                self.sock.close()
            finally:
                self.sock = None

    def _recv_exact(self, n):
        """
        Read exactly n bytes from the socket.

        :param n: Number of bytes to read.
        :return: Bytes read (may be shorter if connection closed).
        """
        buf = b''
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))
            if not chunk:
                break
            buf += chunk
        return buf

    def send_request(self, action, data=None):
        """
        Send a JSON request and wait for a JSON response.

        :param action: Action name (e.g., 'login').
        :param data: Optional dictionary with request data.
        :return: Decoded JSON response as a dict.
        :raises ClientNetworkError: On timeout or other socket errors.
        """
        if not self.sock:
            self.connect()
        payload = json.dumps({'action': action, 'data': data or {}}).encode('utf-8')
        try:
            self.sock.sendall(len(payload).to_bytes(4, 'big') + payload)
            length = self._recv_exact(4)
            if len(length) != 4:
                raise ClientNetworkError('connexion fermée')
            l = int.from_bytes(length, 'big')
            body = self._recv_exact(l)
            return json.loads(body.decode('utf-8'))
        except socket.timeout:
            raise ClientNetworkError('timeout')
        except Exception as exc:
            raise ClientNetworkError(str(exc))


# export simple
__all__ = ['ClientNetwork', 'ClientNetworkError']
