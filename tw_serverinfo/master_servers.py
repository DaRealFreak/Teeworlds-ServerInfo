#!/usr/bin/python
# -*- coding: utf-8 -*-
import socket
from functools import lru_cache
from time import sleep, time

from tw_serverinfo import Network


class MasterServers(object):
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
    _game_servers = []

    @property
    def master_servers(self):
        """Generate generator of master servers with resolve IP address

        :return:
        """
        for master_server in self.master_servers_cfg:
            yield {
                'hostname': master_server['hostname'],
                'ip': socket.gethostbyname(master_server['hostname']),
                'port': master_server['port'],
                'type': 'master'
            }

    @property
    def game_servers(self):
        """Returns the game servers and cache the result

        :return:
        """
        cache_info = self.update_game_servers.cache_info()
        if cache_info.currsize > 0:
            # clear the cache if the last index was more than 10 minutes ago
            if time() >= self.update_game_servers()['timestamp'] + 60 * 10:
                self.update_game_servers.cache_clear()
                self._master_servers = []
                self._game_servers = []
        return self.update_game_servers()

    @lru_cache(maxsize=None)
    def update_game_servers(self):
        """Check the master servers for the game server count and retrieve the server list

        :return:
        """
        # create an udp protocol socket
        sock = socket.socket(family=Network.PROTOCOL_FAMILY, type=socket.SOCK_DGRAM)
        # set the socket to non blocking to allow parallel requests
        sock.setblocking(False)

        for master_server in self.master_servers:
            Network.send_packet(sock=sock, data=Network.PACKETS['SERVERBROWSE_GETCOUNT'], server=master_server)
            Network.send_packet(sock=sock, data=Network.PACKETS['SERVERBROWSE_GETLIST'], server=master_server)

        duration_without_response = Network.CONNECTION_SLEEP_DURATION
        sleep(Network.CONNECTION_SLEEP_DURATION / 1000.0)

        while True:
            if not Network.receive_packet(sock, self.master_servers, self.process_packet):
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
            'servers': self._game_servers,
            'timestamp': time()
        }

    def process_packet(self, data: bytes, server: dict):
        """Process packet function for
         - SERVERBROWSE_COUNT
         - SERVERBROWSE_LIST
        packets

        :type data: bytes
        :type server: dict
        :return:
        """
        server['response'] = True
        self._master_servers.append(server)
        # ToDo: parse the master server response
        self._game_servers.append(data)
