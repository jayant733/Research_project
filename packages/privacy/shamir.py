"""Threshold sharing of one integer over a prime field."""

from typing import List, Sequence, Tuple

PRIME = 2**61 - 1
Share = Tuple[int, int]


def share_secret(
    secret: int, threshold: int, xs: Sequence[int], coefficients: Sequence[int]
) -> List[Share]:
    """Share a secret with a polynomial whose remaining coefficients are supplied."""
    if threshold < 2:
        raise ValueError("Threshold must be at least 2.")
    if len(coefficients) != threshold - 1:
        raise ValueError("Coefficient count does not match the threshold.")
    polynomial = [int(secret) % PRIME] + [int(item) % PRIME for item in coefficients]
    return [(int(x), _evaluate(polynomial, int(x))) for x in xs]


def reconstruct_secret(shares: Sequence[Share]) -> int:
    """Recover the secret from threshold shares with Lagrange interpolation."""
    points = [(int(x) % PRIME, int(y) % PRIME) for x, y in shares]
    secret = 0
    for index, (x_i, y_i) in enumerate(points):
        numerator = 1
        denominator = 1
        for other, (x_j, _y_j) in enumerate(points):
            if index == other:
                continue
            numerator = (numerator * (-x_j)) % PRIME
            denominator = (denominator * (x_i - x_j)) % PRIME
        secret = (secret + y_i * numerator * pow(denominator, -1, PRIME)) % PRIME
    return secret


def split_seed(seed: int) -> Tuple[int, int]:
    value = int(seed)
    return value % PRIME, value // PRIME


def join_seed(low: int, high: int) -> int:
    return (int(high) * PRIME) + int(low)


def _evaluate(polynomial: Sequence[int], x: int) -> int:
    total = 0
    power = 1
    for coefficient in polynomial:
        total = (total + coefficient * power) % PRIME
        power = (power * x) % PRIME
    return total
