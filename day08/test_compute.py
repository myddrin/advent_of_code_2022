import os

import pytest

from .compute import (
    Forest,
    Position,
)


@pytest.fixture(scope='session')
def small_ex_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'small_ex.txt',
    )


@pytest.fixture(scope='session')
def small_ex(small_ex_txt):
    return Forest.from_file(small_ex_txt)


@pytest.fixture(scope='session')
def input_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'input.txt',
    )


class TestTreeMap:

    def test_add_row(self):
        obj = Forest()
        obj._add_row([3, 0, 3, 7, 3], y=0)

        assert obj.height() == 1
        assert obj.length() == 5

        assert obj.map[Position(0, 0)].visible is True, 'on the edge'
        assert obj.map[Position(1, 0)].visible is False, 'smaller left and right'
        assert obj.map[Position(2, 0)].visible is False, 'equal left and smaller right'
        assert obj.map[Position(3, 0)].visible is True, 'tallest'
        assert obj.map[Position(4, 0)].visible is True, 'on the edge'

    def test_add_row_handle_edge_0(self):
        obj = Forest()
        obj._add_row([0, 1, 0, 1, 0], y=0)

        assert obj.height() == 1
        assert obj.length() == 5

        assert obj.map[Position(0, 0)].visible is True, 'on the edge'
        assert obj.map[Position(1, 0)].visible is True
        assert obj.map[Position(2, 0)].visible is False
        assert obj.map[Position(3, 0)].visible is True
        assert obj.map[Position(4, 0)].visible is True

    def test_small_ex(self, small_ex):
        height = small_ex.height()
        length = small_ex.length()
        assert height == 5
        assert length == 5

        # check edges are visible
        for x in range(length):
            assert small_ex.map[Position(x, 0)].visible is True, 'top edge'
            assert small_ex.map[Position(height - 1, 0)].visible is True, 'bottom edge'
        for y in range(height):
            assert small_ex.map[Position(0, y)].visible is True, 'left edge'
            assert small_ex.map[Position(length - 1, y)].visible is True, 'right edge'

        tree_1_1 = small_ex.map[Position(1, 1)]
        assert tree_1_1.visible_left and tree_1_1.visible_up and not (tree_1_1.visible_right or tree_1_1.visible_down)
        assert tree_1_1.visible is True  # left and top
        tree_2_1 = small_ex.map[Position(2, 1)]
        assert tree_2_1.visible_up and tree_2_1.visible_right and not (tree_2_1.visible_left or tree_2_1.visible_down)
        assert tree_2_1.visible is True  # top and right
        assert small_ex.map[Position(3, 1)].visible is False

        tree_1_2 = small_ex.map[Position(1, 2)]
        assert tree_1_2.visible_right and not (tree_1_2.visible_left or tree_1_2.visible_up or tree_1_2.visible_down)
        assert tree_1_2.visible is True  # only right
        assert small_ex.map[Position(2, 2)].visible is False
        tree_3_2 = small_ex.map[Position(3, 2)]
        assert tree_3_2.visible_right and not (tree_3_2.visible_left or tree_3_2.visible_up or tree_3_2.visible_down)
        assert tree_3_2.visible is True  # right

        assert small_ex.map[Position(1, 3)].visible is False
        tree_2_3 = small_ex.map[Position(2, 3)]
        assert tree_2_3.visible_down and tree_2_3.visible_left and not (tree_2_3.visible_up or tree_2_3.visible_right)
        assert tree_2_3.visible is True  # down and left
        assert small_ex.map[Position(3, 3)].visible is False

    def test_get_view(self, small_ex):
        height = small_ex.height()
        length = small_ex.length()

        tree_2_1 = Position(2, 1)
        assert small_ex._get_view(tree_2_1, Position.UP) == 1
        assert small_ex._get_view(tree_2_1, Position.DOWN) == 2
        assert small_ex._get_view(tree_2_1, Position.LEFT) == 1
        assert small_ex._get_view(tree_2_1, Position.RIGHT) == 2

        tree_2_3 = Position(2, 3)
        assert small_ex._get_view(tree_2_3, Position.UP) == 2
        assert small_ex._get_view(tree_2_3, Position.DOWN) == 1
        assert small_ex._get_view(tree_2_3, Position.LEFT) == 2
        assert small_ex._get_view(tree_2_3, Position.RIGHT) == 2

        # top row has 0 looking up
        # bottom row has 0 looking down
        for x in range(length):
            assert small_ex._get_view(Position(x, 0), Position.UP) == 0
            assert small_ex._get_view(Position(x, height - 1), Position.DOWN) == 0

        # left row has 0 looking left
        # right row has 0 looking right
        for y in range(height):
            assert small_ex._get_view(Position(0, y), Position.LEFT) == 0
            assert small_ex._get_view(Position(length - 1, y), Position.RIGHT) == 0

    def test_small_ex_loaded_views(self, small_ex):
        height = small_ex.height()
        length = small_ex.length()
        assert height == 5
        assert length == 5

        # check edges have bad views
        for x in range(length):
            assert small_ex.map[Position(x, 0)].view_score == 0
            assert small_ex.map[Position(height - 1, 0)].view_score == 0
        for y in range(height):
            assert small_ex.map[Position(0, y)].view_score == 0
            assert small_ex.map[Position(length - 1, y)].view_score == 0

        tree_2_1 = Position(2, 1)
        assert small_ex.map[tree_2_1].view_score == 4

        tree_2_3 = Position(2, 3)
        assert small_ex.map[tree_2_3].view_score == 8


class TestQuestion1:

    def test_small_ex(self, small_ex):
        assert len(list(small_ex.visible())) == 21

    def test_input_txt(self, input_txt):
        assert len(list(Forest.from_file(input_txt).visible())) == 1787


class TestQuestion2:

    def test_small_ex(self, small_ex):
        assert small_ex.best_view() == (Position(2, 3), small_ex.map[Position(2, 3)])

    def test_input_txt(self, input_txt):
        assert Forest.from_file(input_txt).best_view()[1].view_score == 440640
