import os

import pytest

from compute import (
    Elf,
    q1_max_carrying_elf,
    q2_top_carrying_elves,
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
def small_ex_elves(small_ex_txt):
    return Elf.load_elves(small_ex_txt)


@pytest.fixture(scope='session')
def input_elves(input_txt):
    return Elf.load_elves(input_txt)


class TestElf:

    def test_load_elves(self, small_ex_txt):
        elves = Elf.load_elves(small_ex_txt)

        assert len(elves) == 5

        assert elves[0].name == 'elf_0'
        assert elves[0].storage == [1000, 2000, 3000]
        assert elves[0].total_storage == 6000

        assert elves[1].name == 'elf_1'
        assert elves[1].storage == [4000]
        assert elves[1].total_storage == 4000

        assert elves[2].name == 'elf_2'
        assert elves[2].storage == [5000, 6000]
        assert elves[2].total_storage == 11000

        assert elves[3].name == 'elf_3'
        assert elves[3].storage == [7000, 8000, 9000]
        assert elves[3].total_storage == 24000

        assert elves[4].name == 'elf_4'
        assert elves[4].storage == [10000]
        assert elves[4].total_storage == 10000

    def test_load_empty_elves(self, tmp_path):
        empty_file = tmp_path / "ex1.txt"
        empty_file.write_text("")

        assert Elf.load_elves(empty_file) == []

    def test_load_no_empty_lines_at_end(self, tmp_path):
        simple_file = tmp_path / "ex1.txt"
        simple_file.write_text("1000")

        elves = Elf.load_elves(simple_file)
        assert len(elves) == 1
        assert elves[0].storage == [1000]

    @pytest.mark.parametrize('content', (
        (),
        (1000, 2000),
        (0,),
    ))
    def test_total_storage(self, content):
        elf = Elf('test_elf', storage=list(content))
        assert elf.total_storage == sum(content)


class TestQuestion1:
    def test_example(self, small_ex_elves):
        most = q1_max_carrying_elf(small_ex_elves)
        assert most.name == 'elf_3'
        assert most.total_storage == 24000

    def test_input(self, input_elves):
        most = q1_max_carrying_elf(input_elves)
        assert most.name == 'elf_171'
        assert most.total_storage == 70509


class TestQuestion2:
    def test_example(self, small_ex_elves):
        top_elves = q2_top_carrying_elves(small_ex_elves)
        assert top_elves.name == 'elf_3, elf_2, elf_4'
        assert top_elves.total_storage == 45000

    def test_input(self, input_elves):
        top_elves = q2_top_carrying_elves(input_elves)
        assert top_elves.name == 'elf_171, elf_79, elf_27'
        assert top_elves.total_storage == 208567
