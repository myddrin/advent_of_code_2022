import os

import pytest

from .compute import (
    Action,
    Cargo,
    Stack,
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


class TestAction:

    @pytest.mark.parametrize('content', (
        'move 1 from 2 to 1',
        'move 10 from 2 to 1'
    ))
    def test_from_str(self, content):
        assert Action.from_str(content).output() == content


class TestStack:

    @pytest.mark.parametrize('content, expected', (
        ('[N]', ['N']),
        ('[N] [C]', ['N', 'C']),
        ('    [D]', [None, 'D']),
        ('    [D]    ', [None, 'D', None]),
        (' 1   2   3 ', []),
    ))
    def test_stacks_from_str(self, content, expected):
        assert Stack.stacks_from_str(content) == expected

    def test_load_stacks(self):
        content = (
            '    [D]',  # in case the file is saved without trailing spaces
            '[N] [C]    ',  # handle a new crate
            '[Z] [M] [P]',
            ' 1   2   3 ',
        )
        stacks = {}
        rv = Stack.load_stacks(content[0], stacks)
        assert rv is True
        assert sorted(stacks.keys()) == [2], 'discovered and populated only middle stack'

        assert Stack.load_stacks(content[1], stacks) is True
        assert sorted(stacks.keys()) == [1, 2]

        assert Stack.load_stacks(content[2], stacks) is True
        assert sorted(stacks.keys()) == [1, 2, 3]

        assert stacks == {
            1: Stack(['Z', 'N']),
            2: Stack(['M', 'C', 'D']),
            3: Stack(['P']),
        }
        assert Stack.load_stacks(content[3], stacks) is False
        assert stacks == {
            1: Stack(['Z', 'N']),
            2: Stack(['M', 'C', 'D']),
            3: Stack(['P']),
        }, 'unchanged'


class TestCrago:

    def test_small_ex(self, small_ex_txt):
        cargo = Cargo.from_file(small_ex_txt)

        assert cargo.stacks == {
            1: Stack(['Z', 'N']),
            2: Stack(['M', 'C', 'D']),
            3: Stack(['P']),
        }
        assert cargo.actions == [
            Action(1, 2, 1),
            Action(3, 1, 3),
            Action(2, 2, 1),
            Action(1, 1, 2),
        ]

    def test_move(self, small_ex_txt):
        cargo = Cargo.from_file(small_ex_txt)

        cargo.move(cargo.actions[0])
        assert cargo.stacks == {
            1: Stack(['Z', 'N', 'D']),
            2: Stack(['M', 'C']),
            3: Stack(['P']),
        }

        cargo.move(cargo.actions[1])
        assert cargo.stacks == {
            1: Stack(),
            2: Stack(['M', 'C']),
            3: Stack(['P', 'D', 'N', 'Z']),
        }

        cargo.move(cargo.actions[2])
        assert cargo.stacks == {
            1: Stack(['C', 'M']),
            2: Stack(),
            3: Stack(['P', 'D', 'N', 'Z']),
        }

        cargo.move(cargo.actions[3])
        assert cargo.stacks == {
            1: Stack(['C']),
            2: Stack(['M']),
            3: Stack(['P', 'D', 'N', 'Z']),
        }

    def test_simultaneous_move(self, small_ex_txt):
        cargo = Cargo.from_file(small_ex_txt)

        cargo.move(cargo.actions[0], simultaneous=True)
        assert cargo.stacks == {
            1: Stack(['Z', 'N', 'D']),
            2: Stack(['M', 'C']),
            3: Stack(['P']),
        }

        cargo.move(cargo.actions[1], simultaneous=True)
        assert cargo.stacks == {
            1: Stack(),
            2: Stack(['M', 'C']),
            3: Stack(['P', 'Z', 'N', 'D']),
        }

        cargo.move(cargo.actions[2], simultaneous=True)
        assert cargo.stacks == {
            1: Stack(['M', 'C']),
            2: Stack(),
            3: Stack(['P', 'Z', 'N', 'D']),
        }

        cargo.move(cargo.actions[3], simultaneous=True)
        assert cargo.stacks == {
            1: Stack(['M']),
            2: Stack(['C']),
            3: Stack(['P', 'Z', 'N', 'D']),
        }

    def test_top_output(self, small_ex_txt):
        cargo = Cargo.from_file(small_ex_txt)
        assert cargo.top_output() == 'NDP'
        cargo = cargo.transform()
        assert cargo.top_output() == 'CMZ'

    def test_transform_is_not_inplace(self, small_ex_txt):
        cargo = Cargo.from_file(small_ex_txt)
        new_cargo = cargo.transform()
        assert cargo is not new_cargo
        assert new_cargo.actions == []
        assert cargo.top_output() == 'NDP'
        assert new_cargo.top_output() == 'CMZ'


class TestQuestion1:
    def test_small_ex(self, small_ex_txt):
        cargo = Cargo.from_file(small_ex_txt).transform()
        assert cargo.top_output() == 'CMZ'

    def test_input(self, input_txt):
        cargo = Cargo.from_file(input_txt).transform()
        assert cargo.top_output() == 'HBTMTBSDC'


class TestQuestion2:
    def test_small_ex(self, small_ex_txt):
        cargo = Cargo.from_file(small_ex_txt).transform(simultaneous=True)
        assert cargo.top_output() == 'MCD'

    def test_input(self, input_txt):
        cargo = Cargo.from_file(input_txt).transform(simultaneous=True)
        assert cargo.top_output() == 'PQTJRSHWS'
