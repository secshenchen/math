"""Exact planar geometry before projection into SVG coordinates."""
from fractions import Fraction


def subtract(a, b):
    return a[0] - b[0], a[1] - b[1]


def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def divide(numerator, denominator):
    return Fraction(numerator) / denominator


def interpolate(a, b, t):
    dx, dy = subtract(b, a)
    return a[0] + t * dx, a[1] + t * dy


def midpoint(a, b):
    return interpolate(a, b, Fraction(1, 2))


def intersection(a, b, c, d):
    ab, cd = subtract(b, a), subtract(d, c)
    determinant = cross(ab, cd)
    if not determinant:
        raise ValueError("Parallel or degenerate lines have no unique intersection")
    return interpolate(a, b, divide(cross(subtract(c, a), cd), determinant))


def area(points):
    following = points[1:] + points[:1]
    return divide(abs(sum(cross(a, b) for a, b in zip(points, following))), 2)
