#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import socket
from collections import deque
from time import sleep

from tw_serverinfo import Network
from tw_serverinfo.models.game_server import GameServer


class GameServers(object):
    """GameServers Class containing the logic to request and parse responses from the game servers"""
    SERVER_CHUNK_SIZE = 50
    SERVER_CHUNK_SLEEP_MS = 1000

    _game_servers = []

    def fill_server_info(self, game_servers: list) -> None:
        """

        :param game_servers:
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
            Network.send_packet(sock=sock, data=Network.PACKETS['SERVERBROWSE_GETINFO'], server=game_server)
            Network.send_packet(sock=sock, data=Network.PACKETS['SERVERBROWSE_GETINFO_64_LEGACY'], server=game_server)

            if i % self.SERVER_CHUNK_SIZE or i >= len(self._game_servers):
                duration_without_response = Network.CONNECTION_SLEEP_DURATION
                sleep(Network.CONNECTION_SLEEP_DURATION / 1000.0)

                while True:
                    if not Network.receive_packet(sock, self._game_servers, self.process_packet):
                        if duration_without_response > Network.CONNECTION_TIMEOUT:
                            # we didn't receive any packets in time and cancel the connection here
                            sock.close()
                            break
                        else:
                            # increase the measured duration without a response and sleep for the set duration
                            duration_without_response += Network.CONNECTION_SLEEP_DURATION
                            sleep(Network.CONNECTION_SLEEP_DURATION / 1000.0)
                    else:
                        # if we got a response reset the duration in case we receive multiple packets
                        duration_without_response = 0

    def process_packet(self, data: bytes, server: GameServer) -> None:
        """Process packet function for
         - SERVERBROWSE_COUNT
         - SERVERBROWSE_LIST
        packets

        :type data: bytes
        :type server: GameServer
        :return:
        """
        slots = deque(data[14:].split(b"\x00"))
        token = int(slots.popleft().decode('utf-8'))
        # ToDo: token validation

        server.response = True

        if data[6:6 + 8] == Network.PACKETS['SERVERBROWSE_INFO']:
            # vanilla
            self.parse_vanilla_response(slots, server)
        elif data[6:6 + 8] == Network.PACKETS['SERVERBROWSE_INFO_64_LEGACY']:
            # 64 legacy
            self.parse_64_legacy_response(slots, server)
        elif data[6:6 + 8] == Network.PACKETS['SERVERBROWSE_INFO_EXTENDED']:
            # extended response, current default of DDNet
            self.parse_extended_response(slots, server)
        elif data[6:6 + 8] == Network.PACKETS['SERVERBROWSE_INFO_EXTENDED_MORE']:
            logging.log(logging.DEBUG, 'no idea what to expect here, never got useful data')

    @staticmethod
    def parse_vanilla_response(slots: deque, server: GameServer) -> None:
        """Parse the default response of the vanilla client

        :param slots:
        :param server:
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
            # no idea what this is, always empty
            server.players.append({
                'name': slots.popleft(),
                'clan': slots.popleft(),
                'country': int(slots.popleft().decode('utf-8')),
                'score': int(slots.popleft().decode('utf-8')),
                'ingame': int(slots.popleft().decode('utf-8'))
            })

    @staticmethod
    def parse_64_legacy_response(slots: deque, server: GameServer) -> None:
        """Parse the 64 slot legacy response

        :param slots:
        :param server:
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

        if slots[0] == b'':
            # no idea what this is, always empty
            slots.popleft()

        while len(slots) >= 5:
            server.players.append({
                'name': slots.popleft(),
                'clan': slots.popleft(),
                'country': int(slots.popleft().decode('utf-8')),
                'score': int(slots.popleft().decode('utf-8')),
                'ingame': int(slots.popleft().decode('utf-8'))
            })

    @staticmethod
    def parse_extended_response(slots: deque, server: GameServer) -> None:
        """Parse the extended server info response(default for DDNet)

        :param slots:
        :param server:
        :return:
        """
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
            server.players.append({
                'name': slots.popleft(),
                'clan': slots.popleft(),
                'country': int(slots.popleft().decode('utf-8')),
                'score': int(slots.popleft().decode('utf-8')),
                'ingame': int(slots.popleft().decode('utf-8'))
            })
