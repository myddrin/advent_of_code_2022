import dataclasses
import re
from argparse import ArgumentParser
from copy import deepcopy
from typing import (
    ClassVar,
    Dict,
    List,
    Optional,
    Self,
)


@dataclasses.dataclass
class Action:
    action_re: ClassVar = re.compile(r'move (\d+) from (\d) to (\d)')

    amount: int
    move_from: int
    move_to: int

    def output(self) -> str:
        return f'move {self.amount} from {self.move_from} to {self.move_to}'

    @classmethod
    def from_str(cls, content: str) -> Self:
        action = cls.action_re.match(content).groups()
        return cls(amount=int(action[0]), move_from=int(action[1]), move_to=int(action[2]))


@dataclasses.dataclass
class Stack:
    crate_re: ClassVar = re.compile(r'\[(.)]')

    crates: List[str] = dataclasses.field(default_factory=list)

    @classmethod
    def stacks_from_str(cls, line: str) -> List[Optional[str]]:
        crates = []
        found_some = False
        while line:
            crate = cls.crate_re.match(line[:3])
            if crate is not None:
                found_some = True
                crates.append(crate.group(1))
            else:
                crates.append(None)
            line = line[4:]
        if found_some:
            return crates
        return []

    @classmethod
    def load_stacks(cls, content: str, stacks: Dict[int, Self]) -> bool:
        current_stack = cls.stacks_from_str(content)
        if not current_stack:
            # When we get an empty list we have to move to load actions
            return False
        for i, content in enumerate(current_stack, start=1):
            if content is not None:
                if i not in stacks:
                    stacks[i] = Stack()
                # can't use `add()` because the loading is reversed
                stacks[i].crates.insert(0, content)

        return True

    def add(self, crate: str):
        self.crates.append(crate)

    def top(self) -> Optional[str]:
        if self.crates:
            return self.crates[-1]
        return None

    def take(self) -> str:
        return self.crates.pop(-1)


@dataclasses.dataclass
class Cargo:
    stacks: Dict[int, Stack]
    actions: List[Action]

    @classmethod
    def from_file(cls, filename: str) -> Self:
        obj = cls(stacks={}, actions=[])
        loading_stacks = True
        print(f'Loading {filename}')
        with open(filename, 'r') as f:
            for line in f:
                content = line.replace('\n', '')

                if loading_stacks:
                    loading_stacks = Stack.load_stacks(content, obj.stacks)
                elif content:
                    obj.actions.append(Action.from_str(content))
        return obj

    def move(self, what: Action, simultaneous=False):
        from_stack = self.stacks[what.move_from]
        to_stack = self.stacks[what.move_to]
        if simultaneous:
            # carry all crates at onces - carry is in reverse order
            carry = [from_stack.take() for _ in range(what.amount)]
            for crate in reversed(carry):
                to_stack.add(crate)
        else:
            for _ in range(what.amount):
                to_stack.add(from_stack.take())

    def transform(self, simultaneous=False) -> Self:
        new_cargo = deepcopy(self)
        new_cargo.actions = []
        for action in self.actions:
            new_cargo.move(action, simultaneous=simultaneous)
        return new_cargo

    def top_output(self):
        return ''.join(
            self.stacks[k].top() or ''
            for k in sorted(self.stacks.keys())
        )


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    orig_cargo = Cargo.from_file(args.input)

    q1_cargo = orig_cargo.transform()
    print(f'q1: top cargo is {q1_cargo.top_output()}')

    q2_cargo = orig_cargo.transform(simultaneous=True)
    print(f'q2: top cargo is {q2_cargo.top_output()}')
