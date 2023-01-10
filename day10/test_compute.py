import os
from typing import List

import pytest

from .compute import (
    Action,
    Display,
    Instruction,
    Pixel,
)


@pytest.fixture(scope='session')
def mini_ex_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'mini_ex.txt',
    )


@pytest.fixture(scope='session')
def small_ex_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'small_ex.txt',
    )


@pytest.fixture(scope='session')
def mini_ex_program(mini_ex_txt) -> List[Instruction]:
    return Instruction.from_file(mini_ex_txt)


@pytest.fixture(scope='session')
def small_ex_program(small_ex_txt) -> List[Instruction]:
    return Instruction.from_file(small_ex_txt)


@pytest.fixture(scope='session')
def input_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'input.txt',
    )


class TestAction:

    @pytest.mark.parametrize('content, expected', (
        ('noop', Instruction(Action.Noop)),
        ('addx 2', Instruction(Action.Addx, 2)),
        ('addx -4', Instruction(Action.Addx, -4)),
        ('addx 10', Instruction(Action.Addx, 10)),
    ))
    def test_from_str(self, content, expected):
        assert Instruction.from_str(content) == expected


class TestInstruction:

    @pytest.mark.parametrize('act', list(Action))
    def test_all_durations(self, act):
        assert Instruction(act).duration > 0


class TestDisplay:

    def test_starts_black(self):
        assert Display().display_str() == [
            ''.join([Pixel.Black.value] * Display.SCREEN_WIDTH),
        ] * Display.SCREEN_HEIGHT

    # def test_mini_ex_txt(self, mini_ex_program):
    #     stat = Display.render_from_program(mini_ex_program)
    #
    #     assert stat.signal_strength == [
    #         1,
    #         4,
    #         -1,
    #     ]

    def test_state_small_ex_txt(self, small_ex_program):
        stat = Display.state_from_program(small_ex_program)

        assert stat.signal_strength == [
            420,
            1140,
            1800,
            2940,
            2880,
            3960,
        ]

    def test_render_small_ex(self, small_ex_program):
        stat = Display.render_from_program(small_ex_program)

        assert stat.interesting_states() == [
            420,
            1140,
            1800,
            2940,
            2880,
            3960,
        ]

    def test_q1(self, input_txt):
        program_data = Instruction.from_file(input_txt)
        display_stats = Display.state_from_program(program_data)
        assert sum(display_stats.signal_strength) == 13480
