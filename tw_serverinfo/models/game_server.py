#!/usr/local/bin/python
# coding: utf-8
from typing import List

from tw_serverinfo.models import Server
from tw_serverinfo.models.player import Player


class GameServer(Server):
    """GameServer Model containing properties for all possibly returned values"""
    _players = []
    _server_type = ''
    _version = ''
    _name = ''
    _map_name = ''
    _map_crc = 0
    _map_size = 0
    _game_type = ''
    _flags = 0
    _num_players = 0
    _max_players = 0
    _num_clients = 0
    _max_clients = 0

    def __init__(self, ip: str, port: int) -> None:
        """Initializing function

        :type ip: str
        :type port: int
        """
        self.ip = ip
        self.port = port
        self.players = []

    def __repr__(self) -> str:
        """Reprint function, displays game server details instead of instance information

        :return:
        """
        return 'GameServer(ip={ip:s}, port={port:d}, response={response!r}, ' \
               'name={name:s}, version={version:s}, map_name={map_name:s}, game_type={game_type:s}, flags={flags:d}, ' \
               'players=({num_players:d}/{max_players:d}), clients=({num_clients:d}/{max_clients:d}), ' \
               'token={token!r}' \
            .format(ip=self.ip, port=self.port, response=self.response,
                    name=self.name, version=self.version, map_name=self.map_name, game_type=self.game_type,
                    flags=self.flags, num_players=self.num_players, max_players=self.max_players,
                    num_clients=self.num_clients, max_clients=self.max_clients, token=self.token)

    @property
    def players(self) -> List[Player]:
        return self._players

    @players.setter
    def players(self, player: List[Player]) -> None:
        self._players = player

    def append_player(self, player: Player) -> None:
        if player not in self._players:
            self._players.append(player)

    @property
    def server_type(self) -> str:
        return self._server_type

    @server_type.setter
    def server_type(self, server_type: str) -> None:
        self._server_type = server_type

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def version(self) -> str:
        return self._version

    @version.setter
    def version(self, version: str) -> None:
        self._version = version

    @property
    def map_name(self) -> str:
        return self._map_name

    @map_name.setter
    def map_name(self, map_name: str) -> None:
        self._map_name = map_name

    @property
    def map_crc(self) -> int:
        return self._map_crc

    @map_crc.setter
    def map_crc(self, map_crc: int) -> None:
        self._map_crc = map_crc

    @property
    def map_size(self) -> int:
        return self._map_size

    @map_size.setter
    def map_size(self, map_size: int) -> None:
        self._map_size = map_size

    @property
    def game_type(self) -> str:
        return self._game_type

    @game_type.setter
    def game_type(self, game_type: str) -> None:
        self._game_type = game_type

    @property
    def flags(self) -> int:
        return self._flags

    @flags.setter
    def flags(self, flags: int) -> None:
        self._flags = flags

    @property
    def num_players(self) -> int:
        return self._num_players

    @num_players.setter
    def num_players(self, num_players: int) -> None:
        self._num_players = num_players

    @property
    def max_players(self) -> int:
        return self._max_players

    @max_players.setter
    def max_players(self, max_players: int) -> None:
        self._max_players = max_players

    @property
    def num_clients(self) -> int:
        return self._num_clients

    @num_clients.setter
    def num_clients(self, num_clients: int) -> None:
        self._num_clients = num_clients

    @property
    def max_clients(self) -> int:
        return self._max_clients

    @max_clients.setter
    def max_clients(self, max_clients: int) -> None:
        self._max_clients = max_clients
