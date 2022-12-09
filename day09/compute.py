import dataclasses
from argparse import ArgumentParser
from collections import defaultdict
from typing import (
    ClassVar,
    Dict,
    List,
    Self,
    Set,
    Tuple,
)


@dataclasses.dataclass(frozen=True)
class Position:
    x: int = 0
    y: int = 0

    UP: ClassVar[Self] = None
    DOWN: ClassVar[Self] = None
    LEFT: ClassVar[Self] = None
    RIGHT: ClassVar[Self] = None
    output: ClassVar[Dict[str, Self]] = {}

    def __add__(self, other: Self) -> Self:
        return Position(
            self.x + other.x,
            self.y + other.y,
        )

    def __sub__(self, other: Self) -> Self:
        return Position(
            self.x - other.x,
            self.y - other.y,
        )

    def is_touching(self, other: Self) -> bool:
        diff = self - other
        return max((
            abs(diff.x),
            abs(diff.y),
        )) <= 1

    def vector(self, other: Self) -> Self:
        # Limit the vector to a move of 1 maximum
        d_x = other.x - self.x
        if d_x != 0:
            d_x = d_x // abs(d_x)
        d_y = other.y - self.y
        if d_y != 0:
            d_y = d_y // abs(d_y)
        return Position(
            d_x,
            d_y,
        )

    @classmethod
    def move_from_str(cls, value: str) -> Tuple[Self, int]:
        direction, amount = value.split(' ')
        offset = cls.output.get(direction)
        if offset is None:
            raise ValueError(f'Unknown direction "{direction}"')
        return offset, int(amount)


Position.UP = Position(0, 1)
Position.DOWN = Position(0, -1)
Position.LEFT = Position(-1, 0)
Position.RIGHT = Position(1, 0)
Position.output['R'] = Position.RIGHT
Position.output['L'] = Position.LEFT
Position.output['U'] = Position.UP
Position.output['D'] = Position.DOWN


@dataclasses.dataclass
class SingleRope:
    head: Position = Position()
    tail: Position = Position()

    def pull(self, new_head: Position):
        self.head = new_head
        self.tail = self._check_pull()

    def _check_pull(self) -> Position:
        if self.head.is_touching(self.tail):
            return self.tail  # touching, don't change the tail

        vector = self.tail.vector(self.head)
        return self.tail + vector


@dataclasses.dataclass
class Rope:
    ropes: List[SingleRope]

    _tail_visited: Set[Position] = dataclasses.field(default_factory=set, repr=False)

    def __post_init__(self):
        # reset the tail_visited to only the position of the tail
        self._tail_visited.add(self.tail)

    def __len__(self):
        return len(self.ropes)

    @property
    def head(self) -> Position:
        return self.ropes[0].head

    @property
    def tail(self) -> Position:
        return self.ropes[-1].tail

    def move(self, offset: Position, n: int, render=False):
        for _ in range(n):
            self.ropes[0].pull(self.head + offset)
            for i in range(1, len(self)):
                previous = i - 1
                self.ropes[i].pull(self.ropes[previous].tail)
            self._tail_visited.add(self.tail)

        if render:
            self.render()

    def render(self):
        # very inefficient rendering...
        max_x = self.tail.x
        min_x = self.tail.x
        max_y = self.tail.y
        min_y = self.tail.y
        known_positions = {}
        cover = defaultdict(list)
        for i, rope in enumerate(self.ropes):
            max_x = max(max_x, rope.head.x)
            min_x = min(min_x, rope.head.x)
            max_y = max(max_y, rope.head.y)
            min_y = min(min_y, rope.head.y)
            if i > 0:
                name = str(i)
            else:
                name = 'H'
            if rope.head not in known_positions:
                known_positions[rope.head] = name
            else:
                cover[known_positions[rope.head]].append(name)

        if self.tail not in known_positions:
            known_positions[self.tail] = 'T'
        else:
            cover[known_positions[self.tail]].append('T')

        print('Current state:')
        for top, others in cover.items():
            print(f'{top} covers {", ".join(others)}')
        if not cover:
            print('No covers')
        for y in range(max_y, min_y - 1, -1):
            line = []
            for x in range(min_x, max_x + 1):
                current = Position(x, y)
                line.append(known_positions.get(current, '.'))
            print(''.join(line))

    def moves_from_file(self, filename: str, render=False) -> int:
        print(f'Loading {filename}')
        with open(filename, 'r') as f:
            for line in f:
                offset, amount = Position.move_from_str(line.replace('\n', ''))
                self.move(offset, amount, render=render)

        return len(self._tail_visited)

    @classmethod
    def single(cls):
        return cls.factory(2)

    @classmethod
    def factory(cls, knots: int) -> Self:
        if knots < 2:
            raise ValueError('Need 2 knots for a rope')
        # We want N knots, each SingleRope is 2 knots
        return cls(ropes=[
            SingleRope()
            for _ in range(knots - 1)
        ])


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    parser.add_argument('--q1-render', action='store_true', default=False, help='Render moves')
    parser.add_argument('--q2-render', action='store_true', default=False, help='Render moves')
    args = parser.parse_args()

    q1 = Rope.single().moves_from_file(args.input, render=args.q1_render)
    print(f'Q1: tail visited {q1} locations')

    q2 = Rope.factory(10).moves_from_file(args.input, render=args.q2_render)
    print(f'Q2: tail visited {q2} locations')
