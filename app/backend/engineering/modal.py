"""Dependency-light modal analysis for symmetric lumped-mass systems."""
from __future__ import annotations
from dataclasses import dataclass
from math import atan2, cos, isfinite, pi, sin, sqrt

@dataclass(frozen=True, slots=True)
class ModalResult:
    eigenvalues: tuple[float, ...]
    angular_frequencies: tuple[float, ...]
    frequencies_hz: tuple[float, ...]
    periods: tuple[float, ...]
    mode_shapes: tuple[tuple[float, ...], ...]


def solve_modes(stiffness: tuple[tuple[float, ...], ...], masses: tuple[float, ...], *, tolerance: float = 1e-10, max_iterations: int = 1000) -> ModalResult:
    size = len(masses)
    if size == 0 or len(stiffness) != size or any(len(row) != size for row in stiffness):
        raise ValueError("stiffness and mass dimensions must match and be non-empty")
    if any(not isfinite(mass) or mass <= 0 for mass in masses):
        raise ValueError("lumped masses must be finite and positive")
    if any(not isfinite(value) for row in stiffness for value in row):
        raise ValueError("stiffness values must be finite")
    if any(abs(stiffness[row][col] - stiffness[col][row]) > tolerance for row in range(size) for col in range(size)):
        raise ValueError("stiffness matrix must be symmetric")
    normalized = [[stiffness[row][col] / sqrt(masses[row] * masses[col]) for col in range(size)] for row in range(size)]
    eigenvalues, vectors = _jacobi_eigendecomposition(normalized, tolerance=tolerance, max_iterations=max_iterations)
    order = tuple(sorted(range(size), key=lambda index: eigenvalues[index]))
    sorted_values = tuple(eigenvalues[index] for index in order)
    if any(value <= tolerance for value in sorted_values):
        raise ValueError("stiffness matrix has zero or negative modal eigenvalues")
    angular = tuple(sqrt(value) for value in sorted_values)
    frequencies = tuple(value / (2.0 * pi) for value in angular)
    periods = tuple(1.0 / value for value in frequencies)
    shapes = tuple(tuple(vectors[row][index] / sqrt(masses[row]) for row in range(size)) for index in order)
    return ModalResult(sorted_values, angular, frequencies, periods, shapes)


def _jacobi_eigendecomposition(matrix: list[list[float]], *, tolerance: float, max_iterations: int) -> tuple[list[float], list[list[float]]]:
    size = len(matrix)
    vectors = [[1.0 if row == col else 0.0 for col in range(size)] for row in range(size)]
    for _ in range(max_iterations):
        magnitude, p, q = max(((abs(matrix[row][col]), row, col) for row in range(size) for col in range(row + 1, size)), default=(0.0, 0, 0))
        if magnitude <= tolerance:
            return [matrix[index][index] for index in range(size)], vectors
        angle = pi / 4.0 if matrix[p][p] == matrix[q][q] else 0.5 * atan2(2.0 * matrix[p][q], matrix[p][p] - matrix[q][q])
        cosine, sine = cos(angle), sin(angle)
        for index in range(size):
            if index not in (p, q):
                aip, aiq = matrix[index][p], matrix[index][q]
                matrix[index][p] = matrix[p][index] = cosine * aip - sine * aiq
                matrix[index][q] = matrix[q][index] = sine * aip + cosine * aiq
            vip, viq = vectors[index][p], vectors[index][q]
            vectors[index][p] = cosine * vip - sine * viq
            vectors[index][q] = sine * vip + cosine * viq
        app, aqq, apq = matrix[p][p], matrix[q][q], matrix[p][q]
        matrix[p][p] = cosine**2 * app - 2.0 * sine * cosine * apq + sine**2 * aqq
        matrix[q][q] = sine**2 * app + 2.0 * sine * cosine * apq + cosine**2 * aqq
        matrix[p][q] = matrix[q][p] = 0.0
    raise ValueError("modal eigen-solver did not converge")