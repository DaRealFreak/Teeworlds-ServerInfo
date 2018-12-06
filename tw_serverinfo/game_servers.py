#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import socket
from collections import deque
from time import sleep
from typing import List

from tw_serverinfo import Network
from tw_serverinfo.models.game_server import GameServer
from tw_serverinfo.models.player import Player


class GameServers(object):
    """GameServers Class containing the logic to request and parse responses from the game servers"""
    SERVER_CHUNK_SIZE = 50
    SERVER_CHUNK_SLEEP_MS = 1000

    _game_servers = []

    def fill_server_info(self, game_servers: List[GameServer]) -> None:
        """Send the SERVERBROWSE_GETINFO and SERVERBROWSE_GETINFO_64_LEGACY packet to each game server in the
        passed game_servers list, parse the response and update the GameServer objects in the game_servers argument

        :type game_servers: list
        :return:
        """
        self._game_servers = game_servers
        # create an udp protocol socket
        sock = socket.socket(family=Network.PROTOCOL_FAMILY, type=socket.SOCK_DGRAM)
        # set the socket to non blocking to allow parallel requests
        sock.setblocking(False)

        i = 0
        for game_server in self._game_servers:  # type: GameServer
            i += 1
            Network.send_packet(sock=sock, data=Network.PACKETS['SERVERBROWSE_GETINFO'], extra_data=b'xe',
                                server=game_server)
            Network.send_packet(sock=sock, data=Network.PACKETS['SERVERBROWSE_GETINFO_64_LEGACY'], extra_data=b'xe',
                                server=game_server)

            if i % self.SERVER_CHUNK_SIZE == 0 or i >= len(self._game_servers):
                duration_without_response = Network.CONNECTION_SLEEP_DURATION
                sleep(Network.CONNECTION_SLEEP_DURATION / 1000.0)

                while duration_without_response < Network.CONNECTION_TIMEOUT:
                    if not Network.receive_packet(sock, self._game_servers, self.process_packet):
                        # increase the measured duration without a response and sleep for the set duration
                        duration_without_response += Network.CONNECTION_SLEEP_DURATION
                        sleep(Network.CONNECTION_SLEEP_DURATION / 1000.0)
                    else:
                        # if we got a response reset the duration in case we receive multiple packets
                        duration_without_response = 0

        # close the socket after checking all servers
        sock.close()

    def process_packet(self, data: bytes, server: GameServer) -> None:
        """Process packet function for
         - SERVERBROWSE_COUNT
         - SERVERBROWSE_LIST
        packets

        :type data: bytes
        :type server: GameServer
        :return:
        """
        server.response = True
        slots = deque(data[14:].split(b"\x00"))

        # validate the server token
        token = int(slots.popleft().decode('utf-8'))
        if int.from_bytes(server.token, byteorder='big') != token & 0xff:
            logging.log(logging.INFO, 'token validation failed for GameServer response. GameServer: ' + str(server))
            return

        if data[6:6 + 8] == Network.PACKETS['SERVERBROWSE_INFO']:
            # vanilla (inf3) packet
            self.parse_vanilla_response(slots, server)
        elif data[6:6 + 8] == Network.PACKETS['SERVERBROWSE_INFO_64_LEGACY']:
            # 64 legacy (dtsf) packet
            self.parse_64_legacy_response(slots, server)
        elif data[6:6 + 8] == Network.PACKETS['SERVERBROWSE_INFO_EXTENDED']:
            # extended response (iext) packet, current default of DDNet
            self.parse_extended_response(slots, server, token)
        elif data[6:6 + 8] == Network.PACKETS['SERVERBROWSE_INFO_EXTENDED_MORE']:
            # extended response (iex+) packet
            self.parse_extended_more_response(slots, server)

    @staticmethod
    def parse_vanilla_response(slots: deque, server: GameServer) -> None:
        """Parse the default response of the vanilla client

        :type slots: deque
        :type server: GameServer
        :return:
        """
        server.server_type = 'vanilla'
        server.version = slots.popleft().decode('utf-8')
        server.name = slots.popleft().decode('utf-8')
        server.map_name = slots.popleft().decode('utf-8')
        server.game_type = slots.popleft().decode('utf-8')
        server.flags = int(slots.popleft().decode('utf-8'))
        server.num_players = int(slots.popleft().decode('utf-8'))
        server.max_players = int(slots.popleft().decode('utf-8'))
        server.num_clients = int(slots.popleft().decode('utf-8'))
        server.max_clients = int(slots.popleft().decode('utf-8'))

        while len(slots) >= 5:
            server.append_player(Player(
                name=slots.popleft().decode('utf-8'),
                clan=slots.popleft().decode('utf-8'),
                country=int(slots.popleft().decode('utf-8')),
                score=int(slots.popleft().decode('utf-8')),
                ingame=bool(int(slots.popleft().decode('utf-8')))
            ))

    @staticmethod
    def parse_64_legacy_response(slots: deque, server: GameServer) -> None:
        """Parse the 64 slot legacy response

        :type slots: deque
        :type server: GameServer
        :return:
        """
        server.server_type = '64_legacy'
        server.version = slots.popleft().decode('utf-8')
        server.name = slots.popleft().decode('utf-8')
        server.map_name = slots.popleft().decode('utf-8')
        server.game_type = slots.popleft().decode('utf-8')
        server.flags = int(slots.popleft().decode('utf-8'))
        server.num_players = int(slots.popleft().decode('utf-8'))
        server.max_players = int(slots.popleft().decode('utf-8'))
        server.num_clients = int(slots.popleft().decode('utf-8'))
        server.max_clients = int(slots.popleft().decode('utf-8'))

        # contains sometimes control bytes or \x00 bytes, not sure what it is
        # since we split at \x00 bytes remove if it is currently \x00 else, split it from the next element
        if slots[0] == b'':
            slots.popleft()
        else:
            slots.appendleft(slots.popleft()[1:])

        while len(slots) >= 5:
            server.append_player(Player(
                name=slots.popleft().decode('utf-8'),
                clan=slots.popleft().decode('utf-8'),
                country=int(slots.popleft().decode('utf-8')),
                score=int(slots.popleft().decode('utf-8')),
                ingame=bool(int(slots.popleft().decode('utf-8')))
            ))

    @staticmethod
    def parse_extended_response(slots: deque, server: GameServer, token: int) -> None:
        """Parse the extended server info response(default for DDNet)

        :type slots: deque
        :type server: GameServer
        :type token: int
        :return:
        """
        if (token & 0xffff00) >> 8 != (server.request_token[0] << 8) + server.request_token[1]:
            # additional server token validation failed
            logging.log(logging.INFO, 'request token validation failed for GameServer response. GameServer: '
                        + str(server))
            return

        server.server_type = 'ext'
        server.version = slots.popleft().decode('utf-8')
        server.name = slots.popleft().decode('utf-8')
        server.map_name = slots.popleft().decode('utf-8')
        server.map_crc = int(slots.popleft().decode('utf-8'))
        server.map_size = int(slots.popleft().decode('utf-8'))
        server.game_type = slots.popleft().decode('utf-8')
        server.flags = int(slots.popleft().decode('utf-8'))
        server.num_players = int(slots.popleft().decode('utf-8'))
        server.max_players = int(slots.popleft().decode('utf-8'))
        server.num_clients = int(slots.popleft().decode('utf-8'))
        server.max_clients = int(slots.popleft().decode('utf-8'))

        while len(slots) >= 6:
            # no idea what this is, always empty
            slots.popleft()
            server.append_player(Player(
                name=slots.popleft().decode('utf-8'),
                clan=slots.popleft().decode('utf-8'),
                country=int(slots.popleft().decode('utf-8')),
                score=int(slots.popleft().decode('utf-8')),
                ingame=bool(int(slots.popleft().decode('utf-8')))
            ))

    @staticmethod
    def parse_extended_more_response(slots: deque, server: GameServer) -> None:
        """Parse the extended server info response(default for DDNet)

        :type slots: deque
        :type server: GameServer
        :return:
        """
        slots.popleft()

        server.server_type = 'ext+'
        while len(slots) >= 6:
            # no idea what this is, always empty
            slots.popleft()
            server.append_player(Player(
                name=slots.popleft().decode('utf-8'),
                clan=slots.popleft().decode('utf-8'),
                country=int(slots.popleft().decode('utf-8')),
                score=int(slots.popleft().decode('utf-8')),
                ingame=bool(int(slots.popleft().decode('utf-8')))
            ))
