#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest

from tw_serverinfo import GameServers
from tw_serverinfo.models.game_server import GameServer


class TestGameServers(unittest.TestCase):

    def setUp(self):
        """Constructor for the Unit Test

        :return:
        """
        self.game_servers_module = GameServers()
        self.game_server = GameServer(ip='95.172.92.151', port=8303)

    def test_fill_server_info(self):
        """Test the fill_server_info function to retrieve and parse data from the the game servers
        if the server responds

        :return:
        """
        self.game_servers_module.fill_server_info([self.game_server])
        if self.game_server.response:
            self.assertTrue(self.game_server.name != '')
            self.assertTrue(self.game_server.max_players > 0)
            self.assertTrue(self.game_server.max_clients > 0)
            self.assertTrue(self.game_server.token != b'')
            self.assertTrue(self.game_server.game_type != '')
            self.assertTrue(self.game_server.map_name != '')


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGameServers)
    unittest.TextTestRunner(verbosity=2).run(suite)
