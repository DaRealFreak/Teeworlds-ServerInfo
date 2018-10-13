#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest

from tw_serverinfo import MasterServers


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
