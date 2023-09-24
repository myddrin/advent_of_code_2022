import dataclasses
import enum
from argparse import ArgumentParser
from enum import Enum
from typing import (
    ClassVar,
    Iterable,
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


class Pixel(enum.Enum):
    Black = '.'
    Lit = '#'


@dataclasses.dataclass
class Display:
    SCREEN_WIDTH: ClassVar[int] = 40
    SCREEN_HEIGHT: ClassVar[int] = 6
    INTERESTING_STATES: ClassVar[Iterable[int]] = (20, 60, 100, 140, 180, 220)

    @staticmethod
    def black_screen_factory(width, height):
        def _f():
            return [Pixel.Black] * (width * height)
        return _f

    signal_strength: List[int] = dataclasses.field(default_factory=list)
    screen_state: List[Pixel] = dataclasses.field(default_factory=black_screen_factory(SCREEN_WIDTH, SCREEN_HEIGHT))
    display_register = 1

    @classmethod
    def signal_strength_from_program(cls, program: List[Instruction]) -> Self:
        """
        `stats.signal_strength` will contain the signal value at the `interesting_states`
        `stats.screen_state` will not be populated
        """
        current_cycle = 1
        stat = cls()
        interesting_states = list(cls.INTERESTING_STATES)  # copy

        for instruction in program:
            prev_reg = stat.display_register

            if instruction.action == Action.Addx:
                stat.display_register += instruction.value

            current_cycle += instruction.duration
            if interesting_states and current_cycle > interesting_states[0]:
                # Using prev_reg as the register changes at the end of the cycle
                stat.signal_strength.append(
                    interesting_states[0] * prev_reg,
                )
                interesting_states.pop(0)

        return stat

    @classmethod
    def screen_state_from_program(cls, program: List[Instruction]) -> Self:
        """
        `stats.signal_strength` will not be populated
        `stats.screen_state` will be populated
        """
        stat = cls()

        current_cycle = 0
        for i, instruction in enumerate(program):
            for cycle in range(instruction.duration):
                stat.render_sprite(current_cycle + cycle)

            if instruction.action == Action.Addx:
                # duration of Addx is 2
                stat.display_register += instruction.value
            elif instruction.action == Action.Noop:
                stat.render_sprite(current_cycle)
            else:
                raise RuntimeError(f'Unexpected op: {instruction.action}')

            current_cycle += instruction.duration

            if len(stat.signal_strength) > (cls.SCREEN_WIDTH * cls.SCREEN_HEIGHT):
                print(f'stop at {i=}')
                break

        return stat

    def render_sprite(self, cycle: int):
        # cycle is starting at 1
        drawing_index = cycle % self.SCREEN_WIDTH
        # the sprite is 3 pixels wide, the center being the display_register
        sprite_location_start = self.display_register - 1
        sprite_location_end = self.display_register + 1
        if sprite_location_start <= drawing_index <= sprite_location_end:
            self.screen_state[cycle] = Pixel.Lit

    def interesting_states(self) -> Optional[List[int]]:
        if self.signal_strength:
            return [
                self.signal_strength[i + 1] * i
                for i in self.INTERESTING_STATES
            ]

    def display_str(self) -> List[str]:
        result = []
        for row in range(self.SCREEN_HEIGHT):
            line = [
                self.screen_state[row * self.SCREEN_WIDTH + col].value
                for col in range(self.SCREEN_WIDTH)
            ]
            result.append(''.join(line))
        return result

    def print_state(self):
        for line in self.display_str():
            print(line)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    program_data = Instruction.from_file(args.input)

    display_stats = Display.signal_strength_from_program(program_data)
    print(f'Q1: signal strength is {sum(display_stats.signal_strength)}')

    screen_rows = Display.screen_state_from_program(program_data).display_str()
    for line in screen_rows:
        # '.' makes it hard to read
        print(line.replace(Pixel.Black.value, ' '))
