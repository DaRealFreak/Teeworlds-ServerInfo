#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This is an example usage
from pprint import pprint

from tw_serverinfo import GameServers
from tw_serverinfo import MasterServers

if __name__ == '__main__':
    m = MasterServers()
    g = GameServers()
    # master server example
    pprint(m.master_servers)
    print('amount of game servers: {amount:d}'.format(amount=len(m.game_servers)))
    # request the server info for the game servers
    g.fill_server_info(m.game_servers)
    for game_server in m.game_servers:
        pprint(game_server)
