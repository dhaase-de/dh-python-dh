"""
Unit tests for `dh.sci`.
"""

import numpy as np
import unittest

import dh.sci


class Test(unittest.TestCase):
    def test_tir(self):
        self.assertEqual(
            dh.sci.tir(np.array([-3.81, 2.97]) * 0.5),
            (-2, 1)
        )
