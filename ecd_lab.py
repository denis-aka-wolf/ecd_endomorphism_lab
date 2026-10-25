"""Учебная арифметика эллиптических кривых y^2 = x^3 + 7 over F_p.

Только стандартная библиотека Python. Предназначено для маленьких полей,
не для криптографически защищённых вычислений.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Iterable

Point = Optional[tuple[int, int]]  # None represents point at infinity


@dataclass(frozen=True)
class Curve:
    p: int
    a: int = 0
    b: int = 7

    def contains(self, P: Point) -> bool:
        if P is None:
            return True
        x, y = P
        return (y * y - (x * x * x + self.a * x + self.b)) % self.p == 0

    def neg(self, P: Point) -> Point:
        if P is None:
            return None
        x, y = P
        return (x, (-y) % self.p)

    def add(self, P: Point, Q: Point) -> Point:
        p = self.p
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q

        if x1 == x2 and (y1 + y2) % p == 0:
            return None

        if P == Q:
            # For y=0, tangent is vertical.
            if y1 % p == 0:
                return None
            numerator = (3 * x1 * x1 + self.a) % p
            denominator = (2 * y1) % p
        else:
            numerator = (y2 - y1) % p
            denominator = (x2 - x1) % p

        # p must be prime and denominator nonzero mod p.
        slope = numerator * pow(denominator, -1, p) % p
        x3 = (slope * slope - x1 - x2) % p
        y3 = (slope * (x1 - x3) - y1) % p
        R = (x3, y3)
        if not self.contains(R):
            raise ArithmeticError("Internal error: addition left the curve")
        return R

    def mul(self, k: int, P: Point) -> Point:
        if k < 0:
            return self.mul(-k, self.neg(P))
        result: Point = None
        addend = P
        while k:
            if k & 1:
                result = self.add(result, addend)
            addend = self.add(addend, addend)
            k >>= 1
        return result

    def enumerate_points(self) -> list[Point]:
        """Enumerate all points, including infinity. Suitable only for small p."""
        points: list[Point] = [None]
        for x in range(self.p):
            rhs = (x**3 + self.a * x + self.b) % self.p
            for y in range(self.p):
                if (y * y) % self.p == rhs:
                    points.append((x, y))
        return points

    def order(self, P: Point) -> int:
        if P is None:
            return 1
        R: Point = None
        for k in range(1, 2 * self.p + 10):
            R = self.add(R, P)
            if R is None:
                return k
        raise RuntimeError("Order bound exceeded; check field and point")


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def cube_roots_of_unity(p: int) -> list[int]:
    return [x for x in range(1, p) if pow(x, 3, p) == 1]


def find_point(curve: Curve) -> tuple[int, int]:
    for P in curve.enumerate_points():
        if P is not None and curve.contains(P):
            return P
    raise ValueError("No affine point found")


def endomorphism(curve: Curve, beta: int, P: Point) -> Point:
    if P is None:
        return None
    if pow(beta, 3, curve.p) != 1:
        raise ValueError("beta must satisfy beta^3 = 1 mod p")
    x, y = P
    return ((beta * x) % curve.p, y)


def orbit(curve: Curve, beta: int, P: Point) -> tuple[Point, ...]:
    """Return unique members of {P,-P,phi(P),-phi(P),phi^2(P),-phi^2(P)}."""
    values: list[Point] = []
    current = P
    for _ in range(3):
        for candidate in (current, curve.neg(current)):
            if candidate not in values:
                values.append(candidate)
        current = endomorphism(curve, beta, current)
    return tuple(values)


def canonical_orbit_key(curve: Curve, beta: int, P: Point) -> tuple:
    """Stable sortable key for an orbit; infinity is represented by (-1,-1)."""
    def key(Q: Point) -> tuple[int, int]:
        return (-1, -1) if Q is None else Q
    return min(key(Q) for Q in orbit(curve, beta, P))


def scalar_table(curve: Curve, G: Point, limit: int | None = None) -> dict[Point, int]:
    """Map each generated point to its first nonnegative scalar."""
    n = curve.order(G)
    stop = n if limit is None else min(n, limit)
    table: dict[Point, int] = {}
    P: Point = None
    for k in range(stop):
        table[P] = k
        P = curve.add(P, G)
    return table


def inspect_orbits(curve: Curve, beta: int, points: Iterable[Point]) -> dict:
    counts: dict[int, int] = {}
    canonical = set()
    total = 0
    for P in points:
        total += 1
        size = len(orbit(curve, beta, P))
        counts[size] = counts.get(size, 0) + 1
        canonical.add(canonical_orbit_key(curve, beta, P))
    return {
        "points_examined": total,
        "orbit_size_histogram": {str(k): v for k, v in sorted(counts.items())},
        "distinct_orbits": len(canonical),
    }
