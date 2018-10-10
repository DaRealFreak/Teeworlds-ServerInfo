#!/usr/bin/python
# -*- coding: utf-8 -*-
import socket
from collections import deque
from time import sleep

from tw_serverinfo import Network


class GameServers(object):
    SERVER_CHUNK_SIZE = 50
    SERVER_CHUNK_SLEEP_MS = 1000

    _game_servers = {}

    def fill_server_info(self, game_servers: dict) -> dict:
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
        for key, game_server in self._game_servers.items():
            i += 1
            game_server = Network.send_packet(sock=sock, data=Network.PACKETS['SERVERBROWSE_GETINFO'],
                                              server=game_server)
            game_server = Network.send_packet(sock=sock, data=Network.PACKETS['SERVERBROWSE_GETINFO_64_LEGACY'],
                                              server=game_server)
            # update game server which got extended by the token
            self._game_servers[key] = game_server

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
        return self._game_servers

    def process_packet(self, data: bytes, server: dict) -> None:
        """Process packet function for
         - SERVERBROWSE_COUNT
         - SERVERBROWSE_LIST
        packets

        :type data: bytes
        :type server: dict
        :return:
        """
        game_server_key = '{ip:s}:{port:d}'.format(ip=server['ip'], port=server['port'])
        server = self._game_servers[game_server_key]

        slots = deque(data[14:].split(b"\x00"))
        token = int(slots.popleft().decode('utf-8'))
        # ToDo: token validation

        if data[6:6 + 8] == Network.PACKETS['SERVERBROWSE_INFO']:
            # vanilla
            updated_server = self.parse_vanilla_response(slots, server)
            self._game_servers[game_server_key] = updated_server
        elif data[6:6 + 8] == Network.PACKETS['SERVERBROWSE_INFO_64_LEGACY']:
            # 64 legacy
            updated_server = self.parse_64_legacy_response(slots, server)
            self._game_servers[game_server_key] = updated_server
        elif data[6:6 + 8] == Network.PACKETS['SERVERBROWSE_INFO_EXTENDED']:
            # extended response, current default of DDNet
            updated_server = self.parse_extended_response(slots, server)
            self._game_servers[game_server_key] = updated_server
        elif data[6:6 + 8] == Network.PACKETS['SERVERBROWSE_INFO_EXTENDED_MORE']:
            print('no idea what to expect here, never got useful data')

    @staticmethod
    def parse_vanilla_response(slots: deque, server: dict) -> dict:
        """Parse the default response of the vanilla client

        :param slots:
        :param server:
        :return:
        """
        version = slots.popleft().decode('utf-8')
        name = slots.popleft().decode('utf-8')
        map_name = slots.popleft().decode('utf-8')
        game_type = slots.popleft().decode('utf-8')
        flags = int(slots.popleft().decode('utf-8'))
        num_players = int(slots.popleft().decode('utf-8'))
        max_players = int(slots.popleft().decode('utf-8'))
        num_clients = int(slots.popleft().decode('utf-8'))
        max_clients = int(slots.popleft().decode('utf-8'))

        players = server['players']
        while len(slots) >= 5:
            # no idea what this is, always empty
            players.append({
                'name': slots.popleft(),
                'clan': slots.popleft(),
                'country': int(slots.popleft().decode('utf-8')),
                'score': int(slots.popleft().decode('utf-8')),
                'ingame': int(slots.popleft().decode('utf-8'))
            })

        return {
            'ip': server['ip'],
            'port': server['port'],
            'type': server['type'],
            'server_type': 'vanilla',
            'version': version,
            'name': name,
            'map_name': map_name,
            'game_type': game_type,
            'flags': flags,
            'num_players': num_players,
            'max_players': max_players,
            'num_clients': num_clients,
            'max_clients': max_clients,
            'players': players
        }

    @staticmethod
    def parse_64_legacy_response(slots: deque, server: dict) -> dict:
        """Parse the 64 slot legacy response

        :param slots:
        :param server:
        :return:
        """
        version = slots.popleft().decode('utf-8')
        name = slots.popleft().decode('utf-8')
        map_name = slots.popleft().decode('utf-8')
        game_type = slots.popleft().decode('utf-8')
        flags = int(slots.popleft().decode('utf-8'))
        num_players = int(slots.popleft().decode('utf-8'))
        max_players = int(slots.popleft().decode('utf-8'))
        num_clients = int(slots.popleft().decode('utf-8'))
        max_clients = int(slots.popleft().decode('utf-8'))

        players = server['players']
        if slots[0] == b'':
            # no idea what this is, always empty
            slots.popleft()

        while len(slots) >= 5:
            player = {
                'name': slots.popleft(),
                'clan': slots.popleft(),
                'country': int(slots.popleft().decode('utf-8')),
                'score': int(slots.popleft().decode('utf-8')),
                'ingame': int(slots.popleft().decode('utf-8'))
            }
            if player not in players:
                players.append(player)

        return {
            'ip': server['ip'],
            'port': server['port'],
            'type': server['type'],
            'server_type': '64_legacy',
            'version': version,
            'name': name,
            'map_name': map_name,
            'game_type': game_type,
            'flags': flags,
            'num_players': num_players,
            'max_players': max_players,
            'num_clients': num_clients,
            'max_clients': max_clients,
            'players': players
        }

    @staticmethod
    def parse_extended_response(slots: deque, server: dict) -> dict:
        """Parse the extended server info response(default for DDNet)

        :param slots:
        :param server:
        :return:
        """
        version = slots.popleft().decode('utf-8')
        name = slots.popleft().decode('utf-8')
        map_name = slots.popleft().decode('utf-8')
        map_crc = int(slots.popleft().decode('utf-8'))
        map_size = int(slots.popleft().decode('utf-8'))
        game_type = slots.popleft().decode('utf-8')
        flags = int(slots.popleft().decode('utf-8'))
        num_players = int(slots.popleft().decode('utf-8'))
        max_players = int(slots.popleft().decode('utf-8'))
        num_clients = int(slots.popleft().decode('utf-8'))
        max_clients = int(slots.popleft().decode('utf-8'))

        players = server['players']
        while len(slots) >= 6:
            # no idea what this is, always empty
            slots.popleft()
            player = {
                'name': slots.popleft(),
                'clan': slots.popleft(),
                'country': int(slots.popleft().decode('utf-8')),
                'score': int(slots.popleft().decode('utf-8')),
                'ingame': int(slots.popleft().decode('utf-8'))
            }
            if player not in players:
                players.append(player)

        return {
            'ip': server['ip'],
            'port': server['port'],
            'type': server['type'],
            'server_type': 'ext',
            'version': version,
            'name': name,
            'map_name': map_name,
            'map_crc': map_crc,
            'map_size': map_size,
            'game_type': game_type,
            'flags': flags,
            'num_players': num_players,
            'max_players': max_players,
            'num_clients': num_clients,
            'max_clients': max_clients,
            'players': players
        }
