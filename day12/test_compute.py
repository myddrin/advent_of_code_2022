import os

import pytest

from .compute import (
    Map,
    Position,
    q2_brute,
)


@pytest.fixture(scope='session')
def small_ex_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'small_ex.txt',
    )


@pytest.fixture(scope='session')
def small_ex_map(small_ex_txt) -> Map:
    return Map.from_file(small_ex_txt)


@pytest.fixture(scope='session')
def input_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'input.txt',
    )


class TestMap:
    def test_load(self, small_ex_map):
        expected = [
            'aabqponm',
            'abcryxxl',
            'accszzxk',
            'acctuvwj',
            'abdefghi',
        ]
        for dy, row in enumerate(expected):
            y = -dy + len(expected) - 1
            for x, cell in enumerate(row):
                exp_elevation = ord(cell) - ord('a')
                assert small_ex_map.elevation_map[Position(x, y)] == exp_elevation
        assert small_ex_map.start == Position(0, 4)
        assert small_ex_map.end == Position(5, 2)


class TestQuestion1:
    def test_small_ex(self, small_ex_map):
        found = small_ex_map.shorted_path()
        assert len(found) == 31 + 1, 'aoc wants to exclude start'
        # there are alt paths so I am too lazy for now
        # assert found == [
        #     Position(0, 4),  # start is excluded from path
        #     (Position(0, 3), Position(1, 4)),
        #     Position(1, 3),
        #     Position(2, 4),
        #     Position(1, 2),
        #     Position(2, 2),
        #     Position(2, 1),
        #     Position(2, 0),
        #     Position(3, 0),
        #     Position(4, 0),
        #     Position(5, 0),
        #     Position(6, 0),
        #     Position(7, 0),
        #     Position(7, 1),
        #     Position(7, 2),
        #     Position(7, 3),
        #     Position(7, 4),
        #     Position(6, 4),
        #     Position(5, 4),
        #     Position(4, 4),
        #     Position(3, 4),
        #     Position(3, 3),
        #     Position(3, 2),
        #     Position(3, 1),
        #     Position(4, 1),
        #     Position(5, 1),
        #     Position(6, 1),
        #     Position(6, 2),
        #     Position(6, 3),
        #     Position(5, 3),
        #     Position(4, 3),
        #     Position(4, 2),
        #     Position(5, 2),  # end
        # ]

    def test_input(self, input_txt):
        assert len(Map.from_file(input_txt).shorted_path()) == 394 + 1, 'answer is -1 because aoc does not want start'


class TestQuestion2:
    def test_small_ex(self, small_ex_map):
        assert len(q2_brute(small_ex_map)) == 29 + 1, 'answer is -1 because aoc does not want start'

    @pytest.mark.slow
    def test_input(self, input_txt):
        assert len(q2_brute(Map.from_file(input_txt))) == 388 + 1, 'answer is -1 because aoc does not want start'
