"""
Unit tests for `dh.image`.
"""

import numpy as np
import unittest

import dh.image


class Test(unittest.TestCase):
    def test_tir(self):
        self.assertEqual(
            dh.image.tir(np.array([-3.81, 2.97]) * 0.5),
            (-2, 1)
        )
