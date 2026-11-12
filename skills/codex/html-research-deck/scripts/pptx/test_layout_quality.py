#!/usr/bin/env python3
"""Unit tests for pure helpers in check_layout_quality.py."""
import unittest
from check_layout_quality import inter_frac, is_pale_tint


class LayoutQualityTests(unittest.TestCase):
    def test_pale_tint_detects_cream_and_pastel_but_not_neutrals(self):
        for tint in ('FDF5E6', 'EDF4F8', 'F7E6EC', 'FFF1D7'):
            self.assertTrue(is_pale_tint(tint), tint)
        for neutral in ('FFFFFF', 'EBEBEB', 'DDDDDD', 'CCCCCC', 'F7F7F7', 'F0F3F5', '000000', '1F77B4', 'E02000'):
            self.assertFalse(is_pale_tint(neutral), neutral)

    def test_inter_frac(self):
        self.assertAlmostEqual(inter_frac([0, 0, 10, 10], [5, 0, 10, 10]), 0.5)
        self.assertEqual(inter_frac([0, 0, 10, 10], [20, 20, 5, 5]), 0)


if __name__ == '__main__':
    unittest.main()
