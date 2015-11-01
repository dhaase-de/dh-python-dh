"""
Unit tests for `dh.utils`.
"""

import numpy as np
import unittest

import dh.utils


class Test(unittest.TestCase):
    def test_flatten_nesting(self):
        """Test flatten() for different nesting levels."""
        self.assertEqual(
            list(dh.utils.flatten(1, [2], [[3]], [4, [5]])),
            [1, 2, 3, 4, 5]
        )

    def test_flatten_tuples(self):
        """Test flatten() for mixed lists and tuples."""
        self.assertEqual(
            list(dh.utils.flatten(1, (2,), [(3,)], ([4, [5]]))),
            [1, 2, 3, 4, 5]
        )

    def test_flatten_types(self):
        """Test flatten() for different types."""
        self.assertEqual(
            list(dh.utils.flatten([[1], ["two"], [3.0], [None], [int]])),
            [1, "two", 3.0, None, int]
        )

    def test_flatten_generator(self):
        """Test flatten() for generators."""
        self.assertEqual(
            list(dh.utils.flatten([x, x**2] for x in range(4))),
            [0, 0, 1, 1, 2, 4, 3, 9]
        )

    def test_flatten_numpy(self):
        """Test flatten() for NumPy arrays."""
        self.assertEqual(
            list(dh.utils.flatten(np.arange(0, 12, dtype="int32").reshape(3, -1))),
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        )
