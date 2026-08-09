"""Dependency-light 2D Euler-Bernoulli frame reference solver.

The kernel supports small-displacement linear elastic axial/flexural members
with three degrees of freedom per node: UX, UY, and rotation about Z.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import hypot, isfinite
from typing import Mapping

@dataclass(frozen=True, slots=True)
class FrameNode2D:
    id: int
    x: float
    y: float
    fix_x: bool = False
    fix_y: bool = False
    fix_rotation: bool = False

@dataclass(frozen=True, slots=True)
class FrameElement2D:
    id: int
    start: int
    end: int
    area: float
    elastic_modulus: float
    moment_of_inertia: float

@dataclass(frozen=True, slots=True)
class LinearFrameResult:
    displacements: Mapping[int, tuple[float, float, float]]
    reactions: Mapping[int, tuple[float, float, float]]
    member_end_forces_local: Mapping[int, tuple[float, float, float, float, float, float]]
    free_dof_residual_max: float


def solve_linear_frame(nodes: tuple[FrameNode2D, ...], elements: tuple[FrameElement2D, ...], loads: Mapping[int, tuple[float, float, float]]) -> LinearFrameResult:
    if not nodes or not elements:
        raise ValueError("a model requires at least one node and one element")
    node_map = {node.id: node for node in nodes}
    if len(node_map) != len(nodes):
        raise ValueError("node ids must be unique")
    if any(not isfinite(value) for node in nodes for value in (node.x, node.y)):
        raise ValueError("node coordinates must be finite")
    ordered_nodes = tuple(sorted(nodes, key=lambda node: node.id))
    ordered_elements = tuple(sorted(elements, key=lambda element: element.id))
    if len({element.id for element in ordered_elements}) != len(ordered_elements):
        raise ValueError("element ids must be unique")
    dof = {node.id: (3 * index, 3 * index + 1, 3 * index + 2) for index, node in enumerate(ordered_nodes)}
    size = 3 * len(ordered_nodes)
    stiffness = [[0.0 for _ in range(size)] for _ in range(size)]
    element_data: dict[int, tuple[FrameElement2D, float, float, float, tuple[int, ...], list[list[float]]]] = {}
    for element in ordered_elements:
        if element.start not in node_map or element.end not in node_map:
            raise ValueError(f"element {element.id} references an unknown node")
        if element.start == element.end or element.area <= 0 or element.elastic_modulus <= 0 or element.moment_of_inertia <= 0:
            raise ValueError(f"element {element.id} has invalid properties")
        if any(not isfinite(value) for value in (element.area, element.elastic_modulus, element.moment_of_inertia)):
            raise ValueError(f"element {element.id} properties must be finite")
        first, second = node_map[element.start], node_map[element.end]
        length = hypot(second.x - first.x, second.y - first.y)
        if length <= 0:
            raise ValueError(f"element {element.id} has zero length")
        c, s = (second.x - first.x) / length, (second.y - first.y) / length
        ea, ei = element.area * element.elastic_modulus, element.elastic_modulus * element.moment_of_inertia
        a, b, d, e = ea / length, 12 * ei / length**3, 6 * ei / length**2, 4 * ei / length
        f = 2 * ei / length
        local = [[a,0,0,-a,0,0],[0,b,d,0,-b,d],[0,d,e,0,-d,f],[-a,0,0,a,0,0],[0,-b,-d,0,b,-d],[0,d,f,0,-d,e]]
        transform = [[c,s,0,0,0,0],[-s,c,0,0,0,0],[0,0,1,0,0,0],[0,0,0,c,s,0],[0,0,0,-s,c,0],[0,0,0,0,0,1]]
        transformed = _mat_t_mat_mat(transform, local)
        indices = (*dof[element.start], *dof[element.end])
        for row, global_row in enumerate(indices):
            for col, global_col in enumerate(indices):
                stiffness[global_row][global_col] += transformed[row][col]
        element_data[element.id] = (element, length, c, s, indices, local)
    force = [0.0] * size
    for node_id, value in loads.items():
        if node_id not in dof or len(value) != 3 or any(not isfinite(item) for item in value):
            raise ValueError(f"invalid load for node {node_id}")
        for index, item in zip(dof[node_id], value):
            force[index] = float(item)
    fixed = {dof[node.id][axis] for node in ordered_nodes for axis, restrained in enumerate((node.fix_x, node.fix_y, node.fix_rotation)) if restrained}
    free = tuple(index for index in range(size) if index not in fixed)
    if not free:
        raise ValueError("model has no free degrees of freedom")
    displacement = [0.0] * size
    solution = _gaussian_solve([[stiffness[row][col] for col in free] for row in free], [force[index] for index in free])
    for index, value in zip(free, solution):
        displacement[index] = value
    residual = [sum(stiffness[row][col] * displacement[col] for col in range(size)) - force[row] for row in range(size)]
    end_forces: dict[int, tuple[float, float, float, float, float, float]] = {}
    for element_id, (_, _, _, _, indices, local) in element_data.items():
        global_displacement = [displacement[index] for index in indices]
        _, length, c, s, _, _ = element_data[element_id]
        transform = [[c,s,0,0,0,0],[-s,c,0,0,0,0],[0,0,1,0,0,0],[0,0,0,c,s,0],[0,0,0,-s,c,0],[0,0,0,0,0,1]]
        local_displacement = [sum(transform[row][col] * global_displacement[col] for col in range(6)) for row in range(6)]
        end_forces[element_id] = tuple(sum(local[row][col] * local_displacement[col] for col in range(6)) for row in range(6))
    return LinearFrameResult(
        displacements={node.id: tuple(displacement[index] for index in dof[node.id]) for node in ordered_nodes},
        reactions={node.id: tuple(residual[index] for index in dof[node.id]) for node in ordered_nodes},
        member_end_forces_local=end_forces,
        free_dof_residual_max=max((abs(residual[index]) for index in free), default=0.0),
    )


def _mat_t_mat_mat(transform: list[list[float]], matrix: list[list[float]]) -> list[list[float]]:
    temp = [[sum(transform[row][k] * matrix[k][col] for k in range(6)) for col in range(6)] for row in range(6)]
    return [[sum(temp[k][row] * transform[k][col] for k in range(6)) for col in range(6)] for row in range(6)]


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