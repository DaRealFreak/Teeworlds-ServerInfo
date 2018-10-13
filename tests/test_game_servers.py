#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest

from tw_serverinfo import GameServers, MasterServers
from tw_serverinfo.models.game_server import GameServer


class TestGameServers(unittest.TestCase):

    def setUp(self):
        """Constructor for the Unit Test

        :return:
        """
        master_servers_module = MasterServers()
        self.game_servers_module = GameServers()
        self.game_servers = master_servers_module.game_servers

    def test_fill_server_info(self):
        """Test the fill_server_info function to retrieve and parse data from the the game servers
        if the server responds

        :return:
        """
        self.game_servers_module.fill_server_info(self.game_servers)
        for game_server in self.game_servers:  # type: GameServer
            if game_server.response:
                self.assertTrue(game_server.name != '')
                self.assertTrue(game_server.max_players > 0)
                self.assertTrue(game_server.max_clients > 0)
                self.assertTrue(game_server.token != b'')
                self.assertTrue(game_server.game_type != '')
                self.assertTrue(game_server.map_name != '')


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGameServers)
    unittest.TextTestRunner(verbosity=2).run(suite)
