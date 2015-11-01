import unittest

import dh.utils

class Test(unittest.TestCase):
    def test_flatten(self):
        self.assertEqual(
            list(dh.utils.flatten(1, [2], [[3]], [4, [5]])),
            [1, 2, 3, 4, 5]
        )
    