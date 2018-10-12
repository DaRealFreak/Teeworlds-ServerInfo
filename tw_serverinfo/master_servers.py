#!/usr/bin/python
# -*- coding: utf-8 -*-
import socket
from functools import lru_cache
from time import sleep, time

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
    def get_master_servers(self) -> list:
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
    def master_servers(self) -> dict:
        """Returns the game servers and cache the result

        :return:
        """
        cache_info = self.update_master_server_info.cache_info()
        if cache_info.currsize > 0:
            # clear the cache if the last index was more than 10 minutes ago
            if time() >= self.update_master_server_info()['timestamp'] + 60 * 10:
                self.update_master_server_info.cache_clear()
        return self.update_master_server_info()

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
            Network.send_packet(sock=sock, data=Network.PACKETS['SERVERBROWSE_GETCOUNT'], server=master_server)
            Network.send_packet(sock=sock, data=Network.PACKETS['SERVERBROWSE_GETLIST'], server=master_server)
            # update master server entry which probably got modified

        duration_without_response = Network.CONNECTION_SLEEP_DURATION
        sleep(Network.CONNECTION_SLEEP_DURATION / 1000.0)

        while True:
            if not Network.receive_packet(sock, self.get_master_servers(), self.process_packet):
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

        return {
            'servers': self._master_servers,
            'timestamp': time()
        }

    @staticmethod
    def process_packet(data: bytes, server: MasterServer) -> None:
        """Process packet function for
         - SERVERBROWSE_COUNT
         - SERVERBROWSE_LIST
        packets

        :type data: bytes
        :type server: dict
        :return:
        """
        server.response = True

        if data[6:6 + 8] == Network.PACKETS['SERVERBROWSE_COUNT']:
            server.num_servers = (data[14] << 8) | data[15]
        elif data[6:6 + 8] == Network.PACKETS['SERVERBROWSE_LIST']:
            for i in range(14, len(data) - 14, 18):
                if data[i:i + 12] == b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff':
                    ip = socket.inet_ntop(socket.AF_INET, data[i + 12:i + 16])
                else:
                    ip = '[' + socket.inet_ntop(socket.AF_INET6, data[i:i + 16]) + ']'

                port = int.from_bytes(data[i + 16:i + 18], byteorder='big')

                game_server = GameServer(ip=ip, port=port)
                server.servers.append(game_server)
