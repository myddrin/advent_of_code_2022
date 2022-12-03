import os
from string import ascii_lowercase
from typing import List

import pytest

from .compute import (
    Compartment,
    Rucksack,
    item_priority,
    q1_priorities,
    q2_badges,
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


@pytest.fixture(scope='session')
def small_ex_rucksacks(small_ex_txt) -> List[Rucksack]:
    return Rucksack.from_file(small_ex_txt)


@pytest.fixture(scope='session')
def input_rucksacks(input_txt) -> List[Rucksack]:
    return Rucksack.from_file(input_txt)


class TestItemPriority:

    def test_lowercase(self):
        for i, letter in enumerate(ascii_lowercase, start=1):
            assert item_priority(letter) == i

    def test_uppercase(self):
        for i, letter in enumerate(ascii_lowercase, start=27):
            assert item_priority(letter.upper()) == i


class TestCompartment:

    def test_from_string(self):
        content = 'vJrwpWtwJgWrhcsFMMfFFhFp'
        a, b = Compartment.from_string(content)

        assert str(a) == ''.join(sorted('vJrwpWtwJgWr'))
        assert str(b) == ''.join(sorted('hcsFMMfFFhFp'))


class TestRucksack:

    def test_small_ex_common(self, small_ex_rucksacks):
        expected_common = 'pLPvts'

        i = 0
        for i, rucksack in enumerate(small_ex_rucksacks, start=1):
            assert rucksack.compartment_1.common(rucksack.compartment_2) == expected_common[i - 1], f'rucksack[{i}]'
        assert i == 6

    def test_small_ex_common_priority(self, small_ex_rucksacks):
        expected_common = (16, 38, 42, 22, 20, 19)

        i = 0
        for i, rucksack in enumerate(small_ex_rucksacks, start=1):
            assert rucksack.common_priority() == expected_common[i - 1], f'rucksack[{i}]'
        assert i == 6

    def test_find_badge(self, small_ex_rucksacks):
        group_a = small_ex_rucksacks[:3]
        group_b = small_ex_rucksacks[3:]
        assert Rucksack.find_badge(group_a) == 'r'
        assert Rucksack.find_badge(group_b) == 'Z'


class TestQuestion1:

    def test_small_ex(self, small_ex_rucksacks):
        assert q1_priorities(small_ex_rucksacks) == 157

    def test_input(self, input_rucksacks):
        assert q1_priorities(input_rucksacks) == 7917


class TestQuestion2:

    def test_small_ex(self, small_ex_rucksacks):
        assert q2_badges(small_ex_rucksacks) == 70

    def test_input(self, input_rucksacks):
        assert q2_badges(input_rucksacks) == 2585
