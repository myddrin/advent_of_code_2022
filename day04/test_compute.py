import os

import pytest

from .compute import (
    Range,
    q1_contains_each_other,
    q2_overlaps,
)


@pytest.fixture(scope='session')
def small_ex_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'small_ex.txt',
    )


@pytest.fixture(scope='session')
def input_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'input.txt',
    )


class TestRange:

    @pytest.mark.parametrize('start, end', (
        (2, 4),
        (10, 120),
    ))
    def test_from_str(self, start, end):
        a = Range.from_str(f'{start}-{end}')
        assert a.start == start
        assert a.end == end

    @pytest.mark.parametrize('a, b, expected', (
        ('2-4', '6-9', False),
        ('5-7', '7-9', False),  # overlap but not contained
        ('2-8', '3-7', False),
        ('3-7', '2-8', True),
        ('6-6', '4-6', True),
        ('4-6', '6-6', False),
        ('7-9', '9-10', False),  # overlap but not contained
    ))
    def test_contains(self, a, b, expected):
        assert (Range.from_str(a) in Range.from_str(b)) is expected

    @pytest.mark.parametrize('a, b, expected', (
        ('2-4', '6-9', False),
        ('5-7', '7-9', True),
        ('2-8', '3-7', True),
        ('3-7', '2-8', True),
        ('6-6', '4-6', True),
        ('4-6', '6-6', True),
        ('7-9', '9-10', True),  # overlap but not contained
    ))
    def test_overlaps_with(self, a, b, expected):
        assert (Range.from_str(a).overlaps_with(Range.from_str(b))) is expected

    def test_from_file(self, small_ex_txt):
        assert Range.from_file(small_ex_txt) == [
            (Range(2, 4), Range(6, 8)),
            (Range(2, 3), Range(4, 5)),
            (Range(5, 7), Range(7, 9)),
            (Range(2, 8), Range(3, 7)),
            (Range(6, 6), Range(4, 6)),
            (Range(2, 6), Range(4, 8)),
        ]


class TestQuestion1:

    def test_small_ex(self, small_ex_txt):
        assert q1_contains_each_other(Range.from_file(small_ex_txt)) == 2

    def test_input(self, input_txt):
        assert q1_contains_each_other(Range.from_file(input_txt)) == 448


class TestQuestion2:

    def test_small_ex(self, small_ex_txt):
        assert q2_overlaps(Range.from_file(small_ex_txt)) == 4

    def test_input(self, input_txt):
        assert q2_overlaps(Range.from_file(input_txt)) == 794
