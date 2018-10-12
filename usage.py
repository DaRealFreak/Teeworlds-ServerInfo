#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This is an example usage
from pprint import pprint

from tw_serverinfo import GameServers
from tw_serverinfo import MasterServers
from tw_serverinfo.models.game_server import GameServer

if __name__ == '__main__':
    m = MasterServers()
    g = GameServers()
    # master server example
    pprint(m.master_servers)
    # game server example using DDNet server
    # DDNet example: 95.172.92.151:8303
    game_server = GameServer(ip='95.172.92.151', port=8303)
    g.fill_server_info([game_server])
    pprint(game_server)
