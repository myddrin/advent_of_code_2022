import os

import pytest

from .compute import (
    Action,
    Result,
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
def small_ex_game_q1(small_ex_txt):
    return Action.from_file(small_ex_txt)


@pytest.fixture(scope='session')
def small_ex_game_q2(small_ex_txt):
    return Action.from_file(small_ex_txt, q1=False)


class TestAction:
    truth = (
        (Action.Rock, Action.Paper, Result.Lose),
        (Action.Rock, Action.Rock, Result.Draw),
        (Action.Rock, Action.Scissor, Result.Win),

        (Action.Paper, Action.Scissor, Result.Lose),
        (Action.Paper, Action.Paper, Result.Draw),
        (Action.Paper, Action.Rock, Result.Win),

        (Action.Scissor, Action.Rock, Result.Lose),
        (Action.Scissor, Action.Scissor, Result.Draw),
        (Action.Scissor, Action.Paper, Result.Win),
    )

    @pytest.mark.parametrize('a, b, exp', truth)
    def test_compare(self, a, b, exp):
        assert a.compare(b) == exp, f'{a.name} vs {b.name} should be {exp.name}'

    @pytest.mark.parametrize('a, b, exp', truth)
    def test_round(self, a, b, exp):
        assert a.round(b) == a.value + exp.value

    def test_small_ex_q1(self, small_ex_game_q1):
        assert small_ex_game_q1 == [
            (Action.Rock, Action.Paper),
            (Action.Paper, Action.Rock),
            (Action.Scissor, Action.Scissor),
        ]
        assert [
            selected.round(opponent)
            for opponent, selected in small_ex_game_q1
        ] == [8, 1, 6]

    def test_small_ex_q2(self, small_ex_game_q2):
        assert small_ex_game_q2 == [
            (Action.Rock, Action.Rock),
            (Action.Paper, Action.Rock),
            (Action.Scissor, Action.Rock),
        ]
        assert [
            selected.round(opponent)
            for opponent, selected in small_ex_game_q2
        ] == [4, 1, 7]

    @pytest.mark.parametrize('a, b, state', truth)
    def test_from_input_q2(self, a, b, state):
        assert Action.from_input_q2(
            b.output,
            state.output
        ) == (b, a), f'{b.name} for {state.name} should mean {a.name}'


class TestQuestion1:
    def test_example(self, small_ex_game_q1):
        assert Action.play(small_ex_game_q1) == 15

    def test_input(self, input_txt):
        input_game = Action.from_file(input_txt)
        assert Action.play(input_game) == 15691


class TestQuestion2:
    def test_example(self, small_ex_game_q2):
        assert Action.play(small_ex_game_q2) == 12

    def test_input(self, input_txt):
        input_game = Action.from_file(input_txt, q1=False)
        assert Action.play(input_game) == 12989
