"""
Unit tests for `dh.sci`.
"""

import numpy as np
import unittest

import dh.sci


class Test(unittest.TestCase):
    def test_tir_generator(self):
        """Test tir() for generators."""
        self.assertEqual(
            dh.sci.tir(float(x) / 2.0 for x in [-3.81, 2.97]),
            (-2, 1)
        )

    def test_tir_numpy(self):
        """Test tir() for NumPy arrays."""
        self.assertEqual(
            dh.sci.tir(0.5 * np.array([-3.81, 2.97])),
            (-2, 1)
        )
