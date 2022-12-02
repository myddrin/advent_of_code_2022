from argparse import ArgumentParser
from enum import IntEnum
from typing import (
    Callable,
    Dict,
    List,
    Self,
    Tuple,
)


class Result(IntEnum):
    Lose = 0
    Draw = 3
    Win = 6

    @classmethod
    def from_input(cls, value: str) -> Self:
        return _result_matrix[value]

    @property
    def output(self):
        if self == Result.Lose:
            return 'X'
        elif self == Result.Draw:
            return 'Y'
        elif self == Result.Win:
            return 'Z'
        else:
            raise NotImplementedError(f'For {self.name}')


# input text to Result
_result_matrix: Dict[str, Result] = {
    obj.output: obj
    for obj in Result
}


Pair = Tuple['Action', 'Action']
Game = List[Pair]


class Action(IntEnum):
    Rock = 1
    Paper = 2
    Scissor = 3

    @classmethod
    def from_input(cls, value: str) -> Self:
        return _action_matrix[value]

    @classmethod
    def from_input_q1(cls, opponent: str, selected: str) -> Pair:
        selected_map = {
            'X': cls.Rock,
            'Y': cls.Paper,
            'Z': cls.Scissor,
        }
        return cls.from_input(opponent), selected_map[selected]

    @classmethod
    def from_input_q2(cls, opponent: str, selected: str) -> Pair:
        adversary = cls.from_input(opponent)
        result = Result.from_input(selected)

        if result == Result.Draw:
            choice = adversary
        elif result == Result.Lose:
            choice = _win_matrix[adversary]
        elif result == Result.Win:
            choice = _rev_win_matrix[adversary]
        else:
            raise NotImplementedError()

        return adversary, choice

    @classmethod
    def from_file(cls, filename: str, q1=True) -> Game:
        print(f'Loading from {filename} using q1={q1}')
        if q1:
            loader: Callable[[str, str], Pair] = Action.from_input_q1
        else:
            loader: Callable[[str, str], Pair] = Action.from_input_q2
        game = []
        with open(filename, 'r') as f:
            for line in f:
                opponent, selected = line.replace('\n', '').split(' ')
                game.append(
                    loader(opponent, selected),
                )

        return game

    @classmethod
    def play(cls, game: Game) -> int:
        score = 0
        for opponent, selected in game:
            score += selected.round(opponent)
        return score

    @property
    def output(self) -> str:
        if self == Action.Rock:
            return 'A'
        elif self == Action.Paper:
            return 'B'
        elif self == Action.Scissor:
            return 'C'
        else:
            raise NotImplementedError(f'For {self.name}')

    def compare(self, other: Self) -> Result:
        """
        :return: 0 if you lost, 3 if the round was a draw, and 6 if you won
        """
        if self == other:
            return Result.Draw
        elif _win_matrix[self] == other:
            return Result.Win
        else:
            return Result.Lose

    def round(self, other: Self) -> int:
        return self.value + self.compare(other).value


# input text to Action
_action_matrix: Dict[str, Action] = {
    obj.output: obj
    for obj in Action
}
# key Action wins over value Action
_win_matrix = {
    Action.Rock: Action.Scissor,
    Action.Scissor: Action.Paper,
    Action.Paper: Action.Rock,
}
# key Action loses against value Action
_rev_win_matrix = {
    v: k
    for k, v in _win_matrix.items()
}


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    q1_game = Action.from_file(args.input)
    q1_score = Action.play(q1_game)
    print(f'q1: score is {q1_score}')

    q2_game = Action.from_file(args.input, q1=False)
    q2_score = Action.play(q2_game)
    print(f'q2: score is {q2_score}')
