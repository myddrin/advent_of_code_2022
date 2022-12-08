import dataclasses
from argparse import ArgumentParser
from typing import (
    ClassVar,
    Dict,
    Iterable,
    Self,
    Tuple,
    Union,
)


@dataclasses.dataclass(frozen=True)
class Position:
    x: int = 0
    y: int = 0

    UP: ClassVar[Self] = None
    DOWN: ClassVar[Self] = None
    LEFT: ClassVar[Self] = None
    RIGHT: ClassVar[Self] = None

    def left(self) -> Self:
        return self + self.LEFT

    def right(self) -> Self:
        return self + self.RIGHT

    def up(self) -> Self:
        return self + self.UP

    def down(self) -> Self:
        return self + self.DOWN

    def __add__(self, other: Self) -> Self:
        return Position(
            self.x + other.x,
            self.y + other.y,
        )


Position.UP = Position(0, -1)
Position.DOWN = Position(0, 1)
Position.LEFT = Position(-1, 0)
Position.RIGHT = Position(1, 0)


@dataclasses.dataclass
class Tree:
    height: int
    # a tree is assumed hidden on all sides
    visible_left: bool = False
    visible_right: bool = False
    visible_up: bool = False
    visible_down: bool = False
    view_score: int = 0

    @property
    def visible(self) -> bool:
        return any((self.visible_left, self.visible_right, self.visible_up, self.visible_down))


@dataclasses.dataclass
class Forest:
    map: Dict[Position, Tree] = dataclasses.field(default_factory=dict)

    def visible(self) -> Iterable[Tree]:
        for tree in self.map.values():
            if tree.visible:
                yield tree

    def length(self) -> int:
        if not self.map:
            return 0
        return max((p.x for p in self.map.keys())) + 1

    def height(self) -> int:
        if not self.map:
            return 0
        return max((p.y for p in self.map.keys())) + 1

    def _add_row(self, row: Iterable[int], y: int):
        x = -1
        tallest_left = -1  # first tree on the edge is always visible, -1 to handle edge tree of size 0
        for x, tree_height in enumerate(row, start=0):
            p = Position(x, y)
            visible = tree_height > tallest_left
            tallest_left = max(tree_height, tallest_left)
            self.map[p] = Tree(height=tree_height, visible_left=visible)

        if x < 0:
            raise RuntimeError(f'Loaded nothing from row {y}')
        p = Position(x, y)
        self.map[p].visible_right = True  # tree on the edge are visible
        tallest_right = self.map[p].height
        x = x - 1
        while x >= 0:
            p = Position(x, y)
            tree = self.map[p]
            tree.visible_right = tree.height > tallest_right
            tallest_right = max(tree.height, tallest_right)
            x = x - 1

    def _get_view(self, start: Position, direction: Position):
        start_height = self.map[start].height
        current = start + direction
        view = 0
        while current in self.map:
            view += 1
            if self.map[current].height >= start_height:
                # reached a taller or same size tree: stop
                return view
            current = current + direction
        return view

    def _update_view_score(self):
        length = self.length()
        height = self.height()
        directions = [
            Position.UP,
            Position.DOWN,
            Position.LEFT,
            Position.RIGHT,
        ]

        for x in range(length):
            for y in range(height):
                current = Position(x, y)
                view = 1
                for dir in directions:
                    view *= self._get_view(current, dir)
                self.map[current].view_score = view

    def best_view(self) -> Tuple[Position, Tree]:
        # we could use `lambda t: t[1].view_score` but this is more obvious
        def _best_pos_tree(t: Tuple[Position, Tree]) -> int:
            return t[1].view_score

        pos, tree = sorted(self.map.items(), key=_best_pos_tree)[-1]
        return pos, tree

    @classmethod
    def from_matrix(cls, data: Iterable[Iterable[Union[Iterable[int], str]]]) -> Self:
        obj = cls()

        for y, row in enumerate(data):
            # insure row is an iterable of int
            obj._add_row(map(int, row), y)  # handles visibility on x axis

        # check visibility on y axis, use -1 to handle case where edge tree is size 0
        length = obj.length()
        height = obj.height()
        tallest_up = [-1] * length
        tallest_down = [-1] * length

        for y in range(height):
            for x in range(length):
                up_tree = obj.map[Position(x, y)]
                up_tree.visible_up = up_tree.height > tallest_up[x]
                tallest_up[x] = max(up_tree.height, tallest_up[x])

                down_tree = obj.map[Position(x, height - y - 1)]
                down_tree.visible_down = down_tree.height > tallest_down[x]
                tallest_down[x] = max(down_tree.height, tallest_down[x])

        obj._update_view_score()
        return obj

    @classmethod
    def from_file(cls, filename: str) -> Self:
        print(f'Loading {filename}')
        with open(filename, 'r') as f:
            return cls.from_matrix(
                map(lambda line: line.replace('\n', ''), f),
            )


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    forest = Forest.from_file(args.input)
    visible = list(forest.visible())
    print(f'Q1: {len(visible)} trees are visible')

    best_view, tree = forest.best_view()
    print(f'Q2: best view is from {best_view} with {tree.view_score} at height {tree.height}')
