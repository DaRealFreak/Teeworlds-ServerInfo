#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This is an example usage
from pprint import pprint

from tw_serverinfo import MasterServers
from tw_serverinfo import GameServers

if __name__ == '__main__':
    m = MasterServers()
    g = GameServers()
    # pprint(m.game_servers)
    # ddnet example: 95.172.92.151:8334
    pprint(g.fill_server_info(
        {
            '95.172.92.151:8334': {
                'ip': '95.172.92.151',
                'port': 8334,
                'type': 'game',
                'players': []
            }
        }
    ))
