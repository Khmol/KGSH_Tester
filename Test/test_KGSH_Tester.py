# -*- encoding: utf-8 -*-

import unittest, sys
import KGSH_Tester
from PyQt5 import QtWidgets

RS_LOOP = False

class TestUM(unittest.TestCase):
    def setUp(self):
        pass

    # def test_Show_Warning_TX_OK(self):
    #     start_index = 7
    #     length = 13
    #     res = self.mainapp.event.Show_Warning_TX_OK(self.rs_receive_pack, start_index, length)
    #     self.assertTrue(res)
    # self.assertEqual(rs_receive_pack, self.b_list[1:])

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
