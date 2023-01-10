import dataclasses
from argparse import ArgumentParser
from enum import Enum
from typing import (
    List,
    Optional,
    Self,
)


class Action(Enum):
    Addx = 'addx'
    Noop = 'noop'


_duration = {
    Action.Addx: 2,
    Action.Noop: 1,
}


@dataclasses.dataclass
class Instruction:
    action: Action
    value: Optional[int] = None

    @property
    def duration(self) -> int:
        return _duration[self.action]

    @classmethod
    def from_str(cls, content: str) -> Self:
        try:
            noop_act = Action(content)
        except ValueError:
            act, value = content.split(' ')
            return Instruction(Action(act), int(value))
        else:
            return Instruction(noop_act, None)

    @classmethod
    def from_file(cls, filename: str) -> List[Self]:
        print(f'Loading {filename}')
        program = []
        with open(filename, 'r') as f:
            for line in f:
                content = line.replace('\n', '')
                program.append(cls.from_str(content))
        return program


@dataclasses.dataclass
class Display:
    signal_strength: List[int] = dataclasses.field(default_factory=list)
    display_register = 1

    @classmethod
    def from_program(cls, program: List[Instruction]) -> Self:
        interesting_states = [20, 60, 100, 140, 180, 220]
        n_instruction = 1
        stat = cls()

        for instruction in program:
            prev_reg = stat.display_register

            if instruction.action == Action.Addx:
                stat.display_register += instruction.value

            n_instruction += instruction.duration
            if interesting_states and n_instruction > interesting_states[0]:
                stat.signal_strength.append(
                    interesting_states[0] * prev_reg,
                )
                interesting_states.pop(0)

        return stat


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    program_data = Instruction.from_file(args.input)

    display_stats = Display.from_program(program_data)
    print(f'Q1: signal strength is {sum(display_stats.signal_strength)}')
