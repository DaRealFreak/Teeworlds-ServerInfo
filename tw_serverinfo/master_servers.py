#!/usr/bin/python
# -*- coding: utf-8 -*-
import socket
from functools import lru_cache
from time import sleep, time
from typing import List

from tw_serverinfo import Network
from tw_serverinfo.models.game_server import GameServer
from tw_serverinfo.models.master_server import MasterServer


class MasterServers(object):
    """MasterServers Class containing the logic to request and parse responses from the master servers"""
    # ToDo: extract to json/yml file
    master_servers_cfg = [
        {
            'hostname': 'master1.teeworlds.com',
            'port': 8300
        },
        {
            'hostname': 'master2.teeworlds.com',
            'port': 8300
        },
        {
            'hostname': 'master3.teeworlds.com',
            'port': 8300
        },
        {
            'hostname': 'master4.teeworlds.com',
            'port': 8300
        }
    ]
    _master_servers = []

    @lru_cache(maxsize=None)
    def get_master_servers(self) -> List[MasterServer]:
        """Generate generator of master servers with resolve IP address

        :return:
        """
        self._master_servers = []
        for master_server in self.master_servers_cfg:
            ip = socket.gethostbyname(master_server['hostname'])
            self._master_servers.append(
                MasterServer(ip=ip, port=master_server['port'], hostname=master_server['hostname'])
            )
        return self._master_servers

    @property
    def master_servers(self) -> List[MasterServer]:
        """Returns the game servers and cache the result

        :return:
        """
        cache_info = self.update_master_server_info.cache_info()
        if cache_info.currsize > 0:
            # clear the cache if the last index was more than 10 minutes ago
            if time() >= self.update_master_server_info()['timestamp'] + 60 * 10:
                self.update_master_server_info.cache_clear()
        return self.update_master_server_info()['servers']

    @property
    def game_servers(self) -> List[GameServer]:
        """Returns the game servers from the updated master server results

        :return:
        """
        game_servers = []
        for master_server in self.master_servers:  # type: MasterServer
            for game_server in master_server.servers:  # type: GameServer
                if game_server not in game_servers:
                    game_servers.append(game_server)
        return game_servers

    @lru_cache(maxsize=None)
    def update_master_server_info(self) -> dict:
        """Check the master servers for the game server count and retrieve the server list

        :return:
        """
        # create an udp protocol socket
        sock = socket.socket(family=Network.PROTOCOL_FAMILY, type=socket.SOCK_DGRAM)
        # set the socket to non blocking to allow parallel requests
        sock.setblocking(False)

        for master_server in self.get_master_servers():
            Network.send_packet(sock=sock, data=Network.PACKETS['SERVERBROWSE_GETCOUNT'], extra_data=b'\xff\xff',
                                server=master_server, add_token=False)
            Network.send_packet(sock=sock, data=Network.PACKETS['SERVERBROWSE_GETLIST'], extra_data=b'\xff\xff',
                                server=master_server, add_token=False)
            # apparently since 06.10.2018 we need the get info packet for the master servers too to retrieve the
            # game servers, normally sent after parsing the response from the previous 2 packets, but works
            # as well if sent directly since no information of the response for the previous 2 packets is needed
            Network.send_packet(sock=sock, data=Network.PACKETS['SERVERBROWSE_GETINFO'], extra_data=b'xe',
                                server=master_server)

        duration_without_response = Network.CONNECTION_SLEEP_DURATION
        sleep(Network.CONNECTION_SLEEP_DURATION / 1000.0)

        while duration_without_response < Network.CONNECTION_TIMEOUT:
            if not Network.receive_packet(sock, self.get_master_servers(), self.process_packet):
                # increase the measured duration without a response and sleep for the set duration
                duration_without_response += Network.CONNECTION_SLEEP_DURATION
                sleep(Network.CONNECTION_SLEEP_DURATION / 1000.0)
            else:
                # if we got a response reset the duration in case we receive multiple packets
                duration_without_response = 0

        # we didn't receive any packets in time and cancel the connection here
        sock.close()

        return {
            'servers': self._master_servers,
            'timestamp': time()
        }

    @staticmethod
    def process_packet(data: bytes, master_server: MasterServer) -> None:
        """Process packet function for
         - SERVERBROWSE_COUNT
         - SERVERBROWSE_LIST
        packets

        :type data: bytes
        :type master_server: dict
        :return:
        """
        master_server.response = True

        if data[6:6 + 8] == Network.PACKETS['SERVERBROWSE_COUNT']:
            MasterServers.parse_count_response(data, master_server)
        elif data[6:6 + 8] == Network.PACKETS['SERVERBROWSE_LIST']:
            MasterServers.parse_list_response(data, master_server)

    @staticmethod
    def parse_count_response(data: bytes, master_server: MasterServer) -> None:
        """Parse the response on the SERVERBROWSE_COUNT packet

        :type data: bytes
        :type master_server: MasterServer
        :return:
        """
        master_server.num_servers = (data[14] << 8) | data[15]

    @staticmethod
    def parse_list_response(data: bytes, master_server: MasterServer) -> None:
        """Parse the response on the SERVERBROWSE_GETLIST and SERVERBROWSE_GETINFO packet

        :type data: bytes
        :type master_server: MasterServer
        :return:
        """
        for i in range(14, len(data) - 14, 18):
            if data[i:i + 12] == b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff':
                ip = socket.inet_ntop(socket.AF_INET, data[i + 12:i + 16])
            else:
                ip = '[' + socket.inet_ntop(socket.AF_INET6, data[i:i + 16]) + ']'

            port = int.from_bytes(data[i + 16:i + 18], byteorder='big')

            if ip != master_server.ip or port != master_server.port:
                game_server = GameServer(ip=ip, port=port)
                master_server.append_server(game_server)
