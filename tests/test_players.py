#!/usr/bin/python
# -*- coding: utf-8 -*-
import random
import unittest

from tw_serverinfo.models.player import Player
from tw_serverinfo.utility import custom_countries


class TestPlayers(unittest.TestCase):

    def test_country_functions(self):
        """Test the country functions since they are the only property containing logic
        instead of plain getters and setters

        :return:
        """
        for custom_country_code in custom_countries.keys():
            p = Player(name='dummy', country=int(custom_country_code))
            self.assertEqual(p.country, custom_countries[custom_country_code]['name'])
            self.assertEqual(p.country_code, custom_countries[custom_country_code]['code'])
            self.assertEqual(p.country_index, int(custom_country_code))

        for i in range(100):
            country_numeric = random.randint(1, 900)
            p = Player(name='dummy', country=country_numeric)
            self.assertIsInstance(p.country, str)
            self.assertIsInstance(p.country_code, str)
            self.assertIsInstance(p.country_index, int)

    def test_repr(self):
        """Test if all attributes in the repr function can get called properly

        :return:
        """
        p1 = Player(name='dummy')
        self.assertIsInstance(p1.__repr__(), str)

    def test_eq(self):
        """Check if equality check works. MasterServer objects with the same ip and same port should
        return True even if another attribute is set

        :return:
        """
        p1 = Player(name='dummy', score=0)
        p2 = Player(name='dummy2', score=1)
        p3 = Player(name='dummy', score=1)
        self.assertEqual(p1, p3)
        self.assertNotEqual(p1, p2)
        self.assertNotEqual(p2, p3)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPlayers)
    unittest.TextTestRunner(verbosity=2).run(suite)
