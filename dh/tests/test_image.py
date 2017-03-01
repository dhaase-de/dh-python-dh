"""
Unit tests for `dh.image`.
"""

import unittest

import numpy as np

import dh.data
import dh.image


class Test(unittest.TestCase):
    def test_stack(self):
        # images
        L = dh.data.lena()
        M = dh.image.convert(dh.data.M(300, 200).astype("uint16"), "uint8")
        G1 = dh.data.grid([350, 500])
        G2 = dh.data.grid([200, 200])
        P = dh.data.pal()

        # test default stacking
        S = dh.image.stack([[L, M], [G1, G2], [P]])
        self.assertEqual(S.shape, (1438, 768, 3))
        self.assertEqual(S.dtype, np.uint8)
        self.assertAlmostEqual(S.mean(), 89.258657616674398)

        # test default stacking with a 1D image vector (one row)
        S = dh.image.stack([L, M, G1, G2, P])
        self.assertEqual(S.shape, (576, 2180, 3))
        self.assertEqual(S.dtype, np.uint8)
        self.assertAlmostEqual(S.mean(), 78.503944741760108)

        # test stacking with padding
        S = dh.image.stack([[L, M], [G1, G2], [P]], padding=32)
        self.assertEqual(S.shape, (1566, 832, 3))
        self.assertEqual(S.dtype, np.uint8)
        self.assertAlmostEqual(S.mean(), 75.658089981006654)

        # test stacking with forced dtype
        S = dh.image.stack([[L, M], [G1, G2], [P]], dtype="float")
        self.assertEqual(S.shape, (1438, 768, 3))
        self.assertEqual(S.dtype, np.float)
        self.assertAlmostEqual(S.mean(), 0.35003395143793881)

        # test stacking with forced gray mode
        S = dh.image.stack([[L, M], [G1, G2], [P]], gray=True)
        self.assertEqual(S.shape, (1438, 768))
        self.assertEqual(S.dtype, np.uint8)
        self.assertAlmostEqual(S.mean(), 89.139465982846545)

    def test_convert(self):
        L = dh.data.lena()

        # test conversion to float
        C = dh.image.convert(L, "float")
        self.assertEqual(C.shape, (512, 512, 3))
        self.assertEqual(C.dtype, np.float)
        self.assertEqual(C.mean(), 0.50285637550104678)

    def test_tir(self):
        self.assertEqual(
            dh.image.tir(np.array([-3.81, 2.97]) * 0.5),
            (-2, 1)
        )

    #def test_