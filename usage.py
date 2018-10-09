#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This is an example usage
from pprint import pprint

from tw_serverinfo import MasterServers

if __name__ == '__main__':
    m = MasterServers()
    pprint(m.game_servers)
