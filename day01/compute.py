import dataclasses
from argparse import ArgumentParser
from operator import attrgetter
from typing import (
    List,
)


@dataclasses.dataclass
class Elf:
    name: str
    storage: List[int] = dataclasses.field(default_factory=list, repr=False)

    @property
    def total_storage(self):
        return sum(self.storage)

    def add(self, value: int):
        self.storage.append(value)

    @classmethod
    def load_elves(cls, filename: str) -> List:
        print(f'Loading {filename}')
        elves = []
        current_elf = Elf(f'elf_{len(elves)}')
        with open(filename, 'r') as f:
            for line in f:
                content = line.replace('\n', '')
                if content:
                    current_elf.add(int(content))
                else:
                    elves.append(current_elf)
                    current_elf = Elf(f'elf_{len(elves)}')

        if current_elf.total_storage > 0:
            elves.append(current_elf)
        return elves


Elves = List[Elf]


def q1_max_carrying_elf(elves: Elves) -> Elf:
    return sorted(elves, key=attrgetter('total_storage'), reverse=True)[0]


def q2_top_carrying_elves(elves: Elves, top=3) -> Elf:
    top_elves = sorted(elves, key=attrgetter('total_storage'), reverse=True)[:top]
    # make a fake elf to simplify
    return Elf(
        name=', '.join((e.name for e in top_elves)),
        storage=[e.total_storage for e in top_elves],
    )


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    parser.add_argument('--q2-top', type=int, default=3, help='Top carrying elves')
    args = parser.parse_args()

    elves = Elf.load_elves(args.input)

    q1 = q1_max_carrying_elf(elves)
    print(f'Most carrying elf is: {q1.name} carrying {q1.total_storage} cal')

    q2 = q2_top_carrying_elves(elves, args.q2_top)
    print(f'Top {args.q2_top} carrying elves are: {q2.name} carrying {q2.total_storage} cal')
