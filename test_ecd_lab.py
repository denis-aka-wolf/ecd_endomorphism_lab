import unittest
from ecd_lab import Curve, cube_roots_of_unity, endomorphism, orbit, scalar_table

class TestECDLab(unittest.TestCase):
    def setUp(self):
        self.curve = Curve(499, 0, 7)
        self.G = (3, 212)
        roots = cube_roots_of_unity(499)
        self.beta = next(r for r in roots if r != 1)

    def test_base_point_on_curve(self):
        self.assertTrue(self.curve.contains(self.G))

    def test_negation(self):
        self.assertIsNone(self.curve.add(self.G, self.curve.neg(self.G)))

    def test_scalar_multiplication_order(self):
        n = self.curve.order(self.G)
        self.assertIsNone(self.curve.mul(n, self.G))
        self.assertIsNotNone(self.curve.mul(n - 1, self.G))

    def test_endomorphism_on_curve(self):
        for P in self.curve.enumerate_points():
            self.assertTrue(self.curve.contains(endomorphism(self.curve, self.beta, P)))

    def test_endomorphism_additive(self):
        points = self.curve.enumerate_points()
        for P in points:
            for Q in points:
                self.assertEqual(
                    endomorphism(self.curve, self.beta, self.curve.add(P, Q)),
                    self.curve.add(endomorphism(self.curve, self.beta, P),
                                   endomorphism(self.curve, self.beta, Q))
                )

    def test_orbit_unique_and_contains_point(self):
        for P in self.curve.enumerate_points():
            O = orbit(self.curve, self.beta, P)
            self.assertIn(P, O)
            self.assertEqual(len(O), len(set(O)))

    def test_scalar_table_roundtrip(self):
        table = scalar_table(self.curve, self.G)
        for k in range(self.curve.order(self.G)):
            self.assertEqual(table[self.curve.mul(k, self.G)], k)

if __name__ == "__main__":
    unittest.main()
