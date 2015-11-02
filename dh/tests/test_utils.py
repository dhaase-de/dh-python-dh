"""
Unit tests for `dh.utils`.
"""

import unittest

import dh.utils


class Test(unittest.TestCase):
    def test_flatten(self):
        self.assertEqual(
            list(dh.utils.flatten(1, ("two",), [[3.0]], [None, [int, []]])),
            [1, "two", 3.0, None, int]
        )

    def test_unique(self):
        x = [1, 2, 1, 3, 3.0, "2", 2, None, False, 1, [], (), [], ()]
        self.assertEqual(
            list(dh.utils.unique(x)),
            [1, 2, 3, "2", None, False, [], ()]
        )

    def test_which(self):
        x = [True, 1, -1, 2, 1.0, float("inf"), [False], {"a": False}, False, 0, 0.0, None, [], {}]
        self.assertEqual(
            list(dh.utils.which(x)),
            [0, 1, 2, 3, 4, 5, 6, 7]
        )
