#!/usr/local/bin/python
# coding: utf-8
from typing import List

from tw_serverinfo.models import Server
from tw_serverinfo.models.game_server import GameServer


class MasterServer(Server):
    """MasterServer Model containing properties for all possibly returned values"""
    _servers: list = []
    _hostname: str = ''
    _num_servers = 0

    def __init__(self, ip: str, port: int, hostname: str = '') -> None:
        """Initializing function

        :type ip: str
        :type port: int
        :type hostname: str
        """
        self._ip = ip
        self._port = port
        self._hostname = hostname

    def __repr__(self) -> str:
        """Reprint function, displays master server details instead of instance information

        :return:
        """
        return 'MasterServer(ip={ip:s}, port={port:d}, hostname={hostname:s}, ' \
               'response={response!r}, num_servers={num_servers:d}, request_token={request_token!r}' \
            .format(ip=self._ip, port=self._port, hostname=self._hostname, response=self._response,
                    num_servers=self._num_servers, request_token=self._request_token)

    @property
    def servers(self) -> List[GameServer]:
        return self._servers

    @servers.setter
    def servers(self, servers: List[GameServer]) -> None:
        self._servers = servers

    def append_server(self, game_server: GameServer) -> None:
        if game_server not in self._servers:
            self._servers.append(game_server)

    @property
    def num_servers(self) -> int:
        return self._num_servers

    @num_servers.setter
    def num_servers(self, number: int) -> None:
        self._num_servers = number
