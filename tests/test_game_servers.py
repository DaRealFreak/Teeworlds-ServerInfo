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

    def test_repr(self):
        """Test if all attributes in the repr function can get called properly

        :return:
        """
        for game_server in self.game_servers:
            self.assertIsInstance(game_server.__repr__(), str)

    def test_eq(self):
        """Check if equality check works. GameServer objects with the same ip and same port should
        return True even if another attribute is set

        :return:
        """
        g1 = GameServer(ip='127.0.0.1', port=8300)
        g2 = GameServer(ip='127.0.0.1', port=8300)
        g2.response = True
        self.assertEqual(g1, g2)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGameServers)
    unittest.TextTestRunner(verbosity=2).run(suite)
