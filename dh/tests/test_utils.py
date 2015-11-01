import unittest

import dh.utils

class Test(unittest.TestCase):
    def test_flatten(self):
        # test nesting of different levels
        self.assertEqual(
            list(dh.utils.flatten(1, [2], [[3]], [4, [5]])),
            [1, 2, 3, 4, 5]
        )
        
        # test nesting using lists and tuples
        self.assertEqual(
            list(dh.utils.flatten(1, (2,), [(3,)], ([4, [5]]))),
            [1, 2, 3, 4, 5]
        )        
        
        # make sure that different types are handled correctly
        self.assertEqual(
            list(dh.utils.flatten([[1], ["two"], [3.0], [None], [int]])),
            [1, "two", 3.0, None, int]
        )
    