import dataclasses
from argparse import ArgumentParser
from typing import (
    Dict,
    List,
    Optional,
    Self,
    Set,
    Tuple,
)


def item_priority(item: str) -> int:
    upper_a = ord('A')  # ascii value of A - 65
    lower_a = ord('a')  # ascii value of a - 97
    if len(item) != 1:
        raise ValueError('Characters only')
    value = ord(item)
    if value < lower_a:
        return (value - upper_a) + 27  # uppercase 27 to 52
    return (value - lower_a) + 1  # lowercase 1 to 26


@dataclasses.dataclass(repr=False)
class Compartment:
    # dict[item -> number of items]
    content: Dict[str, int] = dataclasses.field(default_factory=dict)

    def add(self, item: str):
        if item in self.content:
            self.content[item] += 1
        else:
            self.content[item] = 1

    def unique_items(self) -> Set[str]:
        return set(self.content.keys())

    def __str__(self) -> str:
        return ''.join(sorted([
            k * v
            for k, v in self.content.items()
        ]))

    def common(self, other: Self) -> Optional[str]:
        intersection = set(self.unique_items()).intersection(set(other.unique_items()))
        if intersection:
            return ''.join(intersection)

    @classmethod
    def from_string(cls, value: str) -> Tuple[Self, Self]:
        first = cls()
        second = cls()
        middle = len(value) // 2
        for item in value[:middle]:
            first.add(item)
        for item in value[middle:]:
            second.add(item)
        return first, second


@dataclasses.dataclass
class Rucksack:
    compartment_1: Compartment
    compartment_2: Compartment

    def common_priority(self) -> int:
        common = self.compartment_1.common(self.compartment_2)
        if common:
            # The question says there should only be 1 in common...
            return sum((item_priority(c) for c in common))
        return 0

    def unique_items(self) -> Set[str]:
        return self.compartment_1.unique_items().union(self.compartment_2.unique_items())

    @classmethod
    def from_file(cls, filename: str) -> List[Self]:
        print(f'Loading {filename}')
        rucksacks = []
        with open(filename, 'r') as f:
            for line in f:
                content = line.replace('\n', '')
                if content:  # handle empty last line
                    rucksacks.append(cls(*Compartment.from_string(content)))
        return rucksacks

    @classmethod
    def find_badge(cls, rucksacks: List[Self]) -> Optional[str]:
        content = rucksacks[0].unique_items()
        for rucksack in rucksacks[1:]:
            content = content.intersection(rucksack.unique_items())
        # there should be only 1
        if len(content) == 1:
            return ''.join(content)


def q1_priorities(rucksacks: List[Rucksack]) -> int:
    return sum((rucksack.common_priority() for rucksack in rucksacks))


def q2_badges(rucksacks: List[Rucksack], group_size=3) -> int:
    priorities = 0
    for st in range(0, len(rucksacks), group_size):
        badge = Rucksack.find_badge(rucksacks[st:st + group_size])
        # print(f'Group {st // 3} has badge {badge}')
        priorities += item_priority(badge)
    return priorities


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    loaded = Rucksack.from_file(args.input)

    print(f'Q1 rucksacks priorities: {q1_priorities(loaded)}')
    print(f'Q2 badges priories: {q2_badges(loaded)}')
