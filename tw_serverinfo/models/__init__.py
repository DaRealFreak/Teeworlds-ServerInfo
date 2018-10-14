#!/usr/local/bin/python
# coding: utf-8
import abc


class Server(abc.ABC):
    """Server Model Template, containing properties for same attributes of MasterServer and GameServer objects"""
    _ip: str = ''
    _port: int = 8300
    _response: bool = False
    _token = b''
    _request_token: bytes = b''

    def __eq__(self, other) -> bool:
        """Check for equality of objects

        :type other: Server
        :return:
        """
        return self.ip == other.ip and self.port == other.port

    @property
    def ip(self) -> str:
        return self._ip

    @ip.setter
    def ip(self, ip: str) -> None:
        self._ip = ip

    @property
    def port(self) -> int:
        return self._port

    @port.setter
    def port(self, port: int) -> None:
        self._port = port

    @property
    def response(self) -> bool:
        return self._response

    @response.setter
    def response(self, response: bool) -> None:
        self._response = response

    @property
    def token(self) -> bytes:
        return self._token

    @token.setter
    def token(self, token: bytes) -> None:
        self._token = token

    @property
    def request_token(self) -> bytes:
        return self._request_token

    @request_token.setter
    def request_token(self, token: bytes) -> None:
        self._request_token = token
