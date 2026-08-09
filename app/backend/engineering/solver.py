"""Dependency-light 2D linear truss reference solver."""
from __future__ import annotations
from dataclasses import dataclass
from math import hypot, isfinite
from typing import Mapping

@dataclass(frozen=True, slots=True)
class Node2D:
    id: int
    x: float
    y: float
    fix_x: bool = False
    fix_y: bool = False

@dataclass(frozen=True, slots=True)
class TrussElement2D:
    id: int
    start: int
    end: int
    area: float
    elastic_modulus: float

@dataclass(frozen=True, slots=True)
class LinearTrussResult:
    displacements: Mapping[int, tuple[float, float]]
    reactions: Mapping[int, tuple[float, float]]
    member_forces: Mapping[int, float]


def solve_linear_truss(nodes: tuple[Node2D, ...], elements: tuple[TrussElement2D, ...], loads: Mapping[int, tuple[float, float]]) -> LinearTrussResult:
    if not nodes or not elements:
        raise ValueError("a model requires at least one node and one element")
    node_map = {node.id: node for node in nodes}
    if len(node_map) != len(nodes):
        raise ValueError("node ids must be unique")
    if any(not isfinite(value) for node in nodes for value in (node.x, node.y)):
        raise ValueError("node coordinates must be finite")
    ordered_nodes = tuple(sorted(nodes, key=lambda node: node.id))
    ordered_elements = tuple(sorted(elements, key=lambda item: item.id))
    if len({element.id for element in ordered_elements}) != len(ordered_elements):
        raise ValueError("element ids must be unique")
    dof = {node.id: (2 * index, 2 * index + 1) for index, node in enumerate(ordered_nodes)}
    size = 2 * len(ordered_nodes)
    stiffness = [[0.0 for _ in range(size)] for _ in range(size)]
    geometry: dict[int, tuple[float, float, float]] = {}
    for element in ordered_elements:
        if element.start not in node_map or element.end not in node_map:
            raise ValueError(f"element {element.id} references an unknown node")
        if element.start == element.end or element.area <= 0 or element.elastic_modulus <= 0:
            raise ValueError(f"element {element.id} has invalid geometry or properties")
        if not isfinite(element.area) or not isfinite(element.elastic_modulus):
            raise ValueError(f"element {element.id} properties must be finite")
        first, second = node_map[element.start], node_map[element.end]
        length = hypot(second.x - first.x, second.y - first.y)
        if length <= 0:
            raise ValueError(f"element {element.id} has zero length")
        cx, cy = (second.x - first.x) / length, (second.y - first.y) / length
        geometry[element.id] = (length, cx, cy)
        factor = element.area * element.elastic_modulus / length
        xx, xy, yy = factor * cx * cx, factor * cx * cy, factor * cy * cy
        block = ((xx, xy, -xx, -xy), (xy, yy, -xy, -yy), (-xx, -xy, xx, xy), (-xy, -yy, xy, yy))
        indices = (*dof[element.start], *dof[element.end])
        for row, global_row in enumerate(indices):
            for col, global_col in enumerate(indices):
                stiffness[global_row][global_col] += block[row][col]
    force = [0.0] * size
    for node_id, value in loads.items():
        if node_id not in dof or len(value) != 2 or any(not isfinite(item) for item in value):
            raise ValueError(f"invalid load for node {node_id}")
        force[dof[node_id][0]], force[dof[node_id][1]] = float(value[0]), float(value[1])
    fixed = {dof[node.id][axis] for node in ordered_nodes for axis, restrained in enumerate((node.fix_x, node.fix_y)) if restrained}
    free = tuple(index for index in range(size) if index not in fixed)
    if not free:
        raise ValueError("model has no free degrees of freedom")
    displacement = [0.0] * size
    solution = _gaussian_solve([[stiffness[row][col] for col in free] for row in free], [force[index] for index in free])
    for index, value in zip(free, solution):
        displacement[index] = value
    residual = [sum(stiffness[row][col] * displacement[col] for col in range(size)) - force[row] for row in range(size)]
    member_forces: dict[int, float] = {}
    for element in ordered_elements:
        length, cx, cy = geometry[element.id]
        start_dof, end_dof = dof[element.start], dof[element.end]
        extension = (displacement[end_dof[0]] - displacement[start_dof[0]]) * cx + (displacement[end_dof[1]] - displacement[start_dof[1]]) * cy
        member_forces[element.id] = element.area * element.elastic_modulus / length * extension
    return LinearTrussResult(
        displacements={node.id: (displacement[dof[node.id][0]], displacement[dof[node.id][1]]) for node in ordered_nodes},
        reactions={node.id: (residual[dof[node.id][0]], residual[dof[node.id][1]]) for node in ordered_nodes},
        member_forces=member_forces,
    )


def _gaussian_solve(matrix: list[list[float]], vector: list[float]) -> list[float]:
    n = len(vector)
    augmented = [row[:] + [vector[index]] for index, row in enumerate(matrix)]
    for pivot in range(n):
        pivot_row = max(range(pivot, n), key=lambda row: abs(augmented[row][pivot]))
        if abs(augmented[pivot_row][pivot]) <= 1e-12:
            raise ValueError("singular stiffness matrix; check supports and connectivity")
        augmented[pivot], augmented[pivot_row] = augmented[pivot_row], augmented[pivot]
        scale = augmented[pivot][pivot]
        augmented[pivot] = [value / scale for value in augmented[pivot]]
        for row in range(n):
            if row != pivot:
                factor = augmented[row][pivot]
                if factor:
                    augmented[row] = [left - factor * right for left, right in zip(augmented[row], augmented[pivot])]
    return [augmented[row][n] for row in range(n)]