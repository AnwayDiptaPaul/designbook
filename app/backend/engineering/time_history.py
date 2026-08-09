"""Validated SDOF Newmark-beta time-history integration."""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True, slots=True)
class TimeHistoryResult:
    times: tuple[float, ...]
    displacements: tuple[float, ...]
    velocities: tuple[float, ...]
    accelerations: tuple[float, ...]


def solve_sdof_newmark(mass: float, stiffness: float, damping: float, time_step: float, ground_acceleration: tuple[float, ...], *, beta: float = 0.25, gamma: float = 0.5) -> TimeHistoryResult:
    if any(not isfinite(value) or value <= 0 for value in (mass, stiffness, time_step)):
        raise ValueError("mass, stiffness, and time step must be finite and positive")
    if not isfinite(damping) or damping < 0:
        raise ValueError("damping must be finite and non-negative")
    if not isfinite(beta) or not isfinite(gamma) or beta <= 0 or gamma < 0:
        raise ValueError("Newmark parameters are invalid")
    if not ground_acceleration or any(not isfinite(value) for value in ground_acceleration):
        raise ValueError("ground acceleration must contain finite samples")
    dt = time_step
    a0 = 1.0 / (beta * dt * dt)
    a1 = gamma / (beta * dt)
    a2 = 1.0 / (beta * dt)
    a3 = 1.0 / (2.0 * beta) - 1.0
    a4 = gamma / beta - 1.0
    a5 = dt * (gamma / (2.0 * beta) - 1.0)
    effective_stiffness = stiffness + a0 * mass + a1 * damping
    if effective_stiffness <= 0:
        raise ValueError("effective stiffness must be positive")
    displacements = [0.0]
    velocities = [0.0]
    accelerations = [-ground_acceleration[0]]
    for index in range(1, len(ground_acceleration)):
        previous_u, previous_v, previous_a = displacements[-1], velocities[-1], accelerations[-1]
        effective_force = -mass * ground_acceleration[index] + mass * (a0 * previous_u + a2 * previous_v + a3 * previous_a) + damping * (a1 * previous_u + a4 * previous_v + a5 * previous_a)
        current_u = effective_force / effective_stiffness
        current_a = a0 * (current_u - previous_u) - a2 * previous_v - a3 * previous_a
        current_v = previous_v + dt * ((1.0 - gamma) * previous_a + gamma * current_a)
        displacements.append(current_u)
        velocities.append(current_v)
        accelerations.append(current_a)
    return TimeHistoryResult(
        times=tuple(index * dt for index in range(len(ground_acceleration))),
        displacements=tuple(displacements),
        velocities=tuple(velocities),
        accelerations=tuple(accelerations),
    )
@dataclass(frozen=True, slots=True)
class MultiDofTimeHistoryResult:
    times: tuple[float, ...]
    displacements: tuple[tuple[float, ...], ...]
    velocities: tuple[tuple[float, ...], ...]
    accelerations: tuple[tuple[float, ...], ...]


def solve_mdoF_newmark(mass: tuple[tuple[float, ...], ...], stiffness: tuple[tuple[float, ...], ...], damping: tuple[tuple[float, ...], ...], time_step: float, ground_acceleration: tuple[float, ...], influence: tuple[float, ...], *, beta: float = 0.25, gamma: float = 0.5) -> MultiDofTimeHistoryResult:
    size = len(influence)
    matrices = (mass, stiffness, damping)
    if size == 0 or any(len(matrix) != size or any(len(row) != size for row in matrix) for matrix in matrices):
        raise ValueError("matrix dimensions and influence vector must agree and be non-empty")
    if any(not isfinite(value) for matrix in matrices for row in matrix for value in row) or any(not isfinite(value) for value in influence):
        raise ValueError("multi-DOF inputs must be finite")
    if any(not isfinite(value) or value <= 0 for value in (time_step, beta)) or not isfinite(gamma) or gamma < 0:
        raise ValueError("multi-DOF Newmark parameters are invalid")
    if not ground_acceleration or any(not isfinite(value) for value in ground_acceleration):
        raise ValueError("ground acceleration must contain finite samples")
    dt = time_step
    a0, a1 = 1.0 / (beta * dt * dt), gamma / (beta * dt)
    a2, a3 = 1.0 / (beta * dt), 1.0 / (2.0 * beta) - 1.0
    a4, a5 = gamma / beta - 1.0, dt * (gamma / (2.0 * beta) - 1.0)
    effective = _matrix_add(stiffness, _matrix_add(_matrix_scale(mass, a0), _matrix_scale(damping, a1)))
    displacement = [0.0] * size
    velocity = [0.0] * size
    acceleration = [-influence[row] * ground_acceleration[0] for row in range(size)]
    displacements, velocities, accelerations = [tuple(displacement)], [tuple(velocity)], [tuple(acceleration)]
    for sample in range(1, len(ground_acceleration)):
        previous_u, previous_v, previous_a = displacement[:], velocity[:], acceleration[:]
        inertial = [sum(mass[row][col] * (a0 * previous_u[col] + a2 * previous_v[col] + a3 * previous_a[col]) for col in range(size)) for row in range(size)]
        damping_force = [sum(damping[row][col] * (a1 * previous_u[col] + a4 * previous_v[col] + a5 * previous_a[col]) for col in range(size)) for row in range(size)]
        external = [-sum(mass[row][col] * influence[col] for col in range(size)) * ground_acceleration[sample] for row in range(size)]
        displacement = _solve_linear_system(effective, [external[row] + inertial[row] + damping_force[row] for row in range(size)])
        acceleration = [a0 * (displacement[row] - previous_u[row]) - a2 * previous_v[row] - a3 * previous_a[row] for row in range(size)]
        velocity = [previous_v[row] + dt * ((1.0 - gamma) * previous_a[row] + gamma * acceleration[row]) for row in range(size)]
        displacements.append(tuple(displacement)); velocities.append(tuple(velocity)); accelerations.append(tuple(acceleration))
    return MultiDofTimeHistoryResult(tuple(index * dt for index in range(len(ground_acceleration))), tuple(displacements), tuple(velocities), tuple(accelerations))


def _matrix_scale(matrix: tuple[tuple[float, ...], ...], factor: float) -> tuple[tuple[float, ...], ...]:
    return tuple(tuple(value * factor for value in row) for row in matrix)


def _matrix_add(first: tuple[tuple[float, ...], ...], second: tuple[tuple[float, ...], ...]) -> tuple[tuple[float, ...], ...]:
    return tuple(tuple(left + right for left, right in zip(row_first, row_second)) for row_first, row_second in zip(first, second))


def _solve_linear_system(matrix: tuple[tuple[float, ...], ...], vector: list[float]) -> list[float]:
    size = len(vector)
    augmented = [list(row) + [vector[index]] for index, row in enumerate(matrix)]
    for pivot in range(size):
        pivot_row = max(range(pivot, size), key=lambda row: abs(augmented[row][pivot]))
        if abs(augmented[pivot_row][pivot]) <= 1e-12:
            raise ValueError("singular effective dynamic stiffness matrix")
        augmented[pivot], augmented[pivot_row] = augmented[pivot_row], augmented[pivot]
        scale = augmented[pivot][pivot]
        augmented[pivot] = [value / scale for value in augmented[pivot]]
        for row in range(size):
            if row != pivot:
                factor = augmented[row][pivot]
                if factor:
                    augmented[row] = [left - factor * right for left, right in zip(augmented[row], augmented[pivot])]
    return [augmented[row][size] for row in range(size)]