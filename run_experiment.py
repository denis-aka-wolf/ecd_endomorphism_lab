from __future__ import annotations
import csv
import json
import platform
import sys
from pathlib import Path
from ecd_lab import Curve, cube_roots_of_unity, find_point, orbit, endomorphism, inspect_orbits, scalar_table

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)


def main():
    # p=499 is prime and p ≡ 1 (mod 3), so nontrivial cube roots may exist.
    p = 499
    curve = Curve(p=p, a=0, b=7)
    if not __import__("ecd_lab").is_prime(p):
        raise SystemExit(f"p={p} is not prime")

    roots = cube_roots_of_unity(p)
    nontrivial = [r for r in roots if r != 1]
    if not nontrivial:
        raise SystemExit("No nontrivial cube root of unity found")
    beta = nontrivial[0]

    G = (3, 212)
    if not curve.contains(G):
        raise SystemExit("Configured base point G is not on the curve")
    n = curve.order(G)
    points = curve.enumerate_points()
    table = scalar_table(curve, G)

    # Validate phi(P) is on the curve and respects addition for all points.
    checked_additivity = 0
    for P in points:
        phiP = endomorphism(curve, beta, P)
        if not curve.contains(phiP):
            raise AssertionError(f"phi(P) left curve for P={P}")
        for Q in points:
            lhs = endomorphism(curve, beta, curve.add(P, Q))
            rhs = curve.add(phiP, endomorphism(curve, beta, Q))
            if lhs != rhs:
                raise AssertionError(f"Endomorphism not additive: P={P}, Q={Q}")
            checked_additivity += 1

    generated = [curve.mul(k, G) for k in range(n)]
    orbit_report = inspect_orbits(curve, beta, points)
    scalar_rows = []
    for k, P in enumerate(generated):
        scalar_rows.append({
            "scalar_k": k,
            "x": "" if P is None else P[0],
            "y": "" if P is None else P[1],
            "orbit_key": str(__import__("ecd_lab").canonical_orbit_key(curve, beta, P)),
            "orbit_size": len(orbit(curve, beta, P)),
        })

    with (OUT / "scalar_orbits.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=scalar_rows[0].keys())
        writer.writeheader()
        writer.writerows(scalar_rows)

    report = {
        "python": sys.version,
        "platform": platform.platform(),
        "curve": {"p": p, "a": 0, "b": 7, "equation": "y^2 = x^3 + 7 mod p"},
        "base_point": G,
        "base_point_order": n,
        "curve_point_count": len(points),
        "cube_roots_of_unity": roots,
        "beta": beta,
        "endomorphism_additivity_pair_checks": checked_additivity,
        "orbit_analysis": orbit_report,
        "interpretation": [
            "This is a toy-curve arithmetic experiment, not an ECDLP attack.",
            "Orbit sizes may be smaller than six for special points.",
            "No asymptotic speedup is claimed.",
        ],
    }
    (OUT / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"\nCSV: {OUT / 'scalar_orbits.csv'}")
    print(f"JSON: {OUT / 'report.json'}")


if __name__ == "__main__":
    main()
