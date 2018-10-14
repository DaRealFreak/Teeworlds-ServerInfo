#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest

from tw_serverinfo import MasterServers
from tw_serverinfo.models.master_server import MasterServer


class TestMasterServers(unittest.TestCase):

    def setUp(self):
        """Constructor for the Unit Test

        :return:
        """
        self.master_servers_module = MasterServers()

    def test_master_servers_plain(self):
        """Test the function to retrieve the master servers without requesting information from it yet

        :return:
        """
        self.assertEqual(len(self.master_servers_module._master_servers), 0)
        self.master_servers_module.get_master_servers()
        self.assertEqual(len(self.master_servers_module._master_servers),
                         len(self.master_servers_module.master_servers_cfg))

    def test_repr(self):
        """Test if all attributes in the repr function can get called properly

        :return:
        """
        for master_server in self.master_servers_module.master_servers:
            self.assertIsInstance(master_server.__repr__(), str)

    def test_eq(self):
        """Check if equality check works. MasterServer objects with the same ip and same port should
        return True even if another attribute is set

        :return:
        """
        g1 = MasterServer(ip='127.0.0.1', port=8300)
        g2 = MasterServer(ip='127.0.0.1', port=8300, hostname='master.localhost')
        g3 = MasterServer(ip='127.0.0.2', port=8300, hostname='master.localhost')
        g4 = MasterServer(ip='127.0.0.1', port=8303)
        self.assertEqual(g1, g2)
        self.assertNotEqual(g1, g3)
        self.assertNotEqual(g1, g4)

    def test_master_servers_property(self):
        """Test the function to retrieve and parse data from the master server

        :return:
        """
        # assert that we actually got a dictionary
        self.assertIsInstance(self.master_servers_module.master_servers, list)
        # check length
        self.assertEqual(len(self.master_servers_module.master_servers_cfg),
                         len(self.master_servers_module.master_servers))


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMasterServers)
    unittest.TextTestRunner(verbosity=2).run(suite)
