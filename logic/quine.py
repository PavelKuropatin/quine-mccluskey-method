from collections import defaultdict
from itertools import groupby
from typing import List, Dict, Tuple, Union

from logic.cube import Cube
from utils.constants import ONE, F_FOR_GROUPS


def run_quine_mccluskey(cubes: List[Cube]) -> Tuple[List[Cube], List[int], List[List[int]]]:
    current_cubes: List[Cube] = cubes

    out_cubes: List[Cube] = []
    step: int = 0
    while True:
        grouped_m: Dict[int, List] = group_m_by_f(current_cubes)
        paired_m: List[Tuple[List, List]] = pair_m(grouped_m)

        two_cubes: List[Cube] = get_two_cubes(paired_m, current_cubes)

        if two_cubes:
            if step != 0:
                out_cubes += define_unused_cubes(current_cubes, two_cubes)
        else:
            if step != 0:
                out_cubes += current_cubes
            break

        four_cubes = get_four_cubes(two_cubes)

        if not four_cubes:
            out_cubes += two_cubes
            break

        out_cubes += define_unused_cubes(two_cubes, four_cubes)
        current_cubes = four_cubes
        step += 1

    result_cubes: List[Cube] = out_cubes
    m_with_f_one: List[int] = get_m_with_f_one(cubes)

    matrix: List[List[int]] = build_matrix_for_coverage(result_cubes, m_with_f_one)
    return result_cubes, m_with_f_one, matrix


def build_matrix_for_coverage(result_cubes: List[Cube], m_with_f_one) -> List[List[int]]:
    return [
        [
            1 if cube.has_m(m) else 0
            for m in m_with_f_one
        ]
        for cube in result_cubes
    ]


def get_m_with_f_one(cubes: List[Cube]) -> List[int]:
    return [
        cube.m
        for cube in cubes
        if cube.f == ONE and cube.sum_x
    ]


def define_unused_cubes(prev_cubes: List[Cube], curr_cubes: List[Cube]) -> List[Cube]:
    unused_cubes = []
    for prev_cube in prev_cubes:
        for curr_cube in curr_cubes:
            if not prev_cube.is_covered(curr_cube) and prev_cube not in unused_cubes:
                unused_cubes.append(prev_cube)

    return [
        unused_cube
        for unused_cube in unused_cubes
        if all([
            not unused_cube.is_covered(curr_cube)
            for curr_cube in curr_cubes
        ])
    ]


def get_two_cubes(pairs: List[Tuple[List, List]], cubes: List[Cube]) -> List[Cube]:
    two_cubes = []
    for left_m_set, right_m_set in pairs:
        for i in left_m_set:
            left = find_by_m(cubes, i)
            for j in right_m_set:
                right = find_by_m(cubes, j)
                if left.is_match(right):
                    two_cubes.append(Cube.merge(left, right))

    return two_cubes


def group_m_by_f(cubes: List[Cube]) -> Dict[int, List[int]]:
    """
    group data by count of one in "x" array
    skip cube if its "f" is not in f_values
    return one_count:row_numbers(from "m") dictionary
    """
    cubes: List[Cube] = [cube for cube in cubes if cube.f in F_FOR_GROUPS and cube.sum_x]
    grouped_data = groupby(cubes, lambda row: row.sum_x)
    groups = defaultdict(list)
    for one_count, cubes in grouped_data:
        groups[one_count] += [
            cube.m
            for cube in cubes
        ]
    return groups


def pair_m(groups: Dict[int, List]) -> List[Tuple[List[int], List[int]]]:
    keys = list(sorted(groups.keys()))

    return [
        (groups[keys[i]], groups[keys[i + 1]])
        for i in range(len(keys) - 1)
    ]


def get_four_cubes(two_cubes: List[Cube]) -> List[Cube]:
    four_cubes = []
    for i in range(len(two_cubes)):
        for j in range(i + 1, len(two_cubes)):
            left = two_cubes[i]
            right = two_cubes[j]
            if left.is_match(right):
                cube = Cube.merge(left, right)
                if cube not in four_cubes:
                    four_cubes.append(cube)

    return four_cubes


def find_by_m(cubes: List[Cube], m: Union[List[int]]) -> Union[Cube, None]:
    for cube in cubes:
        if cube.m == m:
            return cube
