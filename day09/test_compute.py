import os

import pytest

from .compute import (
    Position,
    Rope,
    SingleRope,
)


@pytest.fixture(scope='session')
def small_ex_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'small_ex.txt',
    )


@pytest.fixture(scope='session')
def larger_ex_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'larger_ex.txt',
    )


@pytest.fixture(scope='session')
def input_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'input.txt',
    )


class TestPosition:

    @pytest.mark.parametrize('p, o, expected', (
        (Position(0, 0), Position(0, 0), True),  # overlap is touching
        (Position(0, 0), Position(1, 0), True),
        (Position(0, 0), Position(0, 1), True),
        (Position(1, 1), Position(0, 0), True),  # diagonal is touching
        (Position(1, -1), Position(0, 0), True),  # diagonal is touching
        # too far to touch
        (Position(0, 0), Position(2, 0), False),
        (Position(0, 0), Position(0, 2), False),
        (Position(0, 0), Position(1, 2), False),
        (Position(0, 0), Position(2, 2), False),
    ))
    def test_is_touching(self, p, o, expected):
        assert p.is_touching(o) is expected
        assert p.is_touching(o) is expected, 'reciprocity'
        # with offset
        for offset in (Position(5, 0), Position(0, 3), Position(-4, -3)):
            p_prime = p + offset
            o_prime = o + offset
            assert p_prime.is_touching(o_prime) is expected, f'with {offset=}'
            assert o_prime.is_touching(p_prime) is expected, f'reciprocity with {offset=}'


class TestSingleRope:

    @pytest.mark.parametrize('h, exp', (
        (Position(1, 0), Position(0, 0)),  # touching
        (Position(2, 0), Position(1, 0)),
        (Position(1, 1), Position(0, 0)),  # touching
        (Position(1, 2), Position(1, 1)),  # diagonal
        (Position(2, 1), Position(1, 1)),  # diagonal
    ))
    def test_check_pull(self, h, exp):
        rope = SingleRope(head=h, tail=Position(0, 0))
        assert rope._check_pull() == exp, f'{rope=}'
        # with offset
        for offset in (Position(5, 0), Position(0, 3), Position(-4, -3)):
            rope_prime = SingleRope(head=h + offset, tail=offset)
            assert rope_prime._check_pull() == exp + offset, f'with {offset=}'

    @classmethod
    def move(cls, rope: SingleRope, offset: Position, n: int):
        for _ in range(n):
            rope.pull(rope.head + offset)

    def test_move(self):
        # Testing small_ex step by step
        rope = SingleRope()

        self.move(rope, Position.RIGHT, 4)
        assert rope.head == Position(4, 0)
        assert rope.tail == Position(3, 0)

        self.move(rope, Position.UP, 2)  # original example is UP 4
        assert rope.head == Position(4, 2)
        assert rope.tail == Position(4, 1)  # diagonal move
        self.move(rope, Position.UP, 2)
        assert rope.head == Position(4, 4)
        assert rope.tail == Position(4, 3)

        self.move(rope, Position.LEFT, 2)  # original example is LEFT 3
        assert rope.head == Position(2, 4)
        assert rope.tail == Position(3, 4)  # diagonal move
        self.move(rope, Position.LEFT, 1)
        assert rope.head == Position(1, 4)
        assert rope.tail == Position(2, 4)

        self.move(rope, Position.DOWN, 1)
        assert rope.head == Position(1, 3)
        assert rope.tail == Position(2, 4), 'unmoved'

        self.move(rope, Position.RIGHT, 2)  # original is RIGHT 4
        assert rope.head == Position(3, 3)
        assert rope.tail == Position(2, 4), 'unmoved'
        self.move(rope, Position.RIGHT, 2)
        assert rope.head == Position(5, 3)
        assert rope.tail == Position(4, 3)  # diagonal + move

        self.move(rope, Position.DOWN, 1)
        assert rope.head == Position(5, 2)
        assert rope.tail == Position(4, 3), 'unmoved'

        self.move(rope, Position.LEFT, 2)  # original is LEFT 5
        assert rope.head == Position(3, 2)
        assert rope.tail == Position(4, 3), 'unmoved'
        self.move(rope, Position.LEFT, 3)  # original is LEFT 5
        assert rope.head == Position(0, 2)
        assert rope.tail == Position(1, 2)  # diagonal + move

        self.move(rope, Position.RIGHT, 2)
        assert rope.head == Position(2, 2)
        assert rope.tail == Position(1, 2), 'unmoved'


class TestRope:

    def test_small_ex_q1(self):
        rope = Rope.single()

        rope.move(Position.RIGHT, 4)
        assert rope.head == Position(4, 0)
        assert rope.tail == Position(3, 0)

        rope.move(Position.UP, 2)  # original example is UP 4
        assert rope.head == Position(4, 2)
        assert rope.tail == Position(4, 1)  # diagonal move
        rope.move(Position.UP, 2)
        assert rope.head == Position(4, 4)
        assert rope.tail == Position(4, 3)

        rope.move(Position.LEFT, 2)  # original example is LEFT 3
        assert rope.head == Position(2, 4)
        assert rope.tail == Position(3, 4)  # diagonal move
        rope.move(Position.LEFT, 1)
        assert rope.head == Position(1, 4)
        assert rope.tail == Position(2, 4)

        rope.move(Position.DOWN, 1)
        assert rope.head == Position(1, 3)
        assert rope.tail == Position(2, 4), 'unmoved'

        rope.move(Position.RIGHT, 2)  # original is RIGHT 4
        assert rope.head == Position(3, 3)
        assert rope.tail == Position(2, 4), 'unmoved'
        rope.move(Position.RIGHT, 2)
        assert rope.head == Position(5, 3)
        assert rope.tail == Position(4, 3)  # diagonal + move

        rope.move(Position.DOWN, 1)
        assert rope.head == Position(5, 2)
        assert rope.tail == Position(4, 3), 'unmoved'

        rope.move(Position.LEFT, 2)  # original is LEFT 5
        assert rope.head == Position(3, 2)
        assert rope.tail == Position(4, 3), 'unmoved'
        rope.move(Position.LEFT, 3)  # original is LEFT 5
        assert rope.head == Position(0, 2)
        assert rope.tail == Position(1, 2)  # diagonal + move

        rope.move(Position.RIGHT, 2)
        assert rope.head == Position(2, 2)
        assert rope.tail == Position(1, 2), 'unmoved'


class TestQuestion1:

    def test_small_ex(self, small_ex_txt):
        assert Rope.single().moves_from_file(small_ex_txt) == 13

    def test_input(self, input_txt):
        assert Rope.single().moves_from_file(input_txt) == 6023


class TestQuestion2:
    def test_small_ex(self, small_ex_txt):
        assert Rope.factory(10).moves_from_file(small_ex_txt) == 1

    def test_larger_ex(self, larger_ex_txt):
        assert Rope.factory(10).moves_from_file(larger_ex_txt) == 36

    def test_input(self, input_txt):
        assert Rope.factory(10).moves_from_file(input_txt) == 2533
