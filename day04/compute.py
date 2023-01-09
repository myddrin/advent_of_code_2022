import dataclasses
from argparse import ArgumentParser
from typing import (
    List,
    Self,
    Tuple,
)


@dataclasses.dataclass(frozen=True)
class Range:
    start: int
    end: int

    def __contains__(self, item: Self) -> bool:
        return self.start <= item.start <= self.end and self.start <= item.end <= self.end

    def overlaps_with(self, other: Self) -> bool:
        return any((
            self.start <= other.start <= self.end,
            self.start <= other.end <= self.end,
            other.start <= self.start <= other.end,
            other.start <= self.end <= other.end,
        ))

    @classmethod
    def from_str(cls, range: str) -> Self:
        start, end = range.split('-')
        return cls(int(start), int(end))

    @classmethod
    def from_file(cls, filename: str) -> List[Tuple[Self, Self]]:
        print(f'Loading from {filename}')
        data = []
        with open(filename, 'r') as f:
            for line in f:
                content = line.replace('\n', '')
                a, b = content.split(',')
                data.append((
                    cls.from_str(a),
                    cls.from_str(b),
                ))
        return data


def q1_contains_each_other(data: List[Tuple[Range, Range]]) -> int:
    result = 0
    for a, b in data:
        if a in b or b in a:
            result += 1
    return result


def q2_overlaps(data: List[Tuple[Range, Range]]) -> int:
    result = 0
    for a, b in data:
        if a.overlaps_with(b):
            result += 1
    return result


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    entries = Range.from_file(args.input)
    print(f'Loaded {len(entries)} pairs')
    contained = q1_contains_each_other(entries)
    print(f'Q1: {contained} pairs contain the other')

    overlaps = q2_overlaps(entries)
    print(f'Q2: {overlaps} pairs overlap with the other')
