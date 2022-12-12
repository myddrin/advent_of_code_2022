import dataclasses
from argparse import ArgumentParser
from operator import attrgetter
from typing import (
    ClassVar,
    Dict,
    Iterable,
    List,
    Optional,
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

    def __str__(self):
        return f'({self.x}, {self.y})'

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


Position.UP = Position(0, 1)
Position.DOWN = Position(0, -1)
Position.LEFT = Position(-1, 0)
Position.RIGHT = Position(1, 0)


@dataclasses.dataclass
class GraphVertex:
    position: Position
    neighbours: List[Position]

    distance: Optional[int] = None  # None means infinity
    previous: Optional[Position] = None  # None means it's the start position


@dataclasses.dataclass
class Map:
    START_CHAR: ClassVar[str] = 'S'
    DEST_CHAR: ClassVar[str] = 'E'
    BASE_ELEVATION: ClassVar[int] = ord('a')

    # position to elevation
    elevation_map: Dict[Position, int]
    start: Position
    end: Position

    def _travel_cost(self, a: Position, b: Position) -> Optional[int]:
        elevation_a = self.elevation_map[a]
        elevation_b = self.elevation_map[b]
        if elevation_b > elevation_a and elevation_b - elevation_a > 1:
            return None  # too high
        return 1  # accessible

    def iter_graph_vertices(self) -> Iterable[GraphVertex]:
        for position in self.elevation_map.keys():
            neighbours = []
            for direction in (Position.UP, Position.DOWN, Position.LEFT, Position.RIGHT):
                where = position + direction
                if where in self.elevation_map and self._travel_cost(position, where) is not None:
                    neighbours.append(where)
            yield GraphVertex(
                position=position,
                neighbours=neighbours,
            )

    def shorted_path(self, start: Position = None) -> List[Position]:
        if start is None:
            start = self.start
        # Using Dijkstra's algorithm
        vertices: Dict[Position, GraphVertex] = {
            v.position: v
            for v in self.iter_graph_vertices()
        }  # keep a copy alive until the end
        uncomputed: Dict[Position, GraphVertex] = {
            k: v
            for k, v in vertices.items()
        }  # Q in Dijkstra
        uncomputed_with_distance: Set[Position] = set()

        uncomputed[start].distance = 0
        uncomputed_with_distance.add(start)

        print(f'Computing shortest path between {start} and {self.end}')
        steps = 1
        while uncomputed:
            current_candidates = [
                uncomputed[k]
                for k in uncomputed_with_distance
            ]
            if steps % 1000 == 0:
                print(f'{steps=} with {len(current_candidates)} uncomputed candidate')
            if not current_candidates:
                print('Only infinity nodes are left!')
                break  # only infinity nodes are left
            current = sorted(
                current_candidates,
                key=attrgetter('distance')
            )[0]

            uncomputed.pop(current.position)
            uncomputed_with_distance.remove(current.position)

            for neighbour in current.neighbours:
                if neighbour not in uncomputed:
                    continue
                candidate = current.distance + self._travel_cost(current.position, neighbour)
                if uncomputed[neighbour].distance is None or candidate < uncomputed[neighbour].distance:
                    uncomputed[neighbour].distance = candidate
                    uncomputed[neighbour].previous = current.position
                    uncomputed_with_distance.add(neighbour)
            steps += 1
        print(f'Solved {start} to {self.end} in {steps} steps')

        shortest_path = []
        current = self.end
        while current is not None:
            shortest_path.append(current)
            current = vertices[current].previous
        if shortest_path[-1] != start:
            return []  # no path
        return list(reversed(shortest_path))

    @classmethod
    def elevation(cls, char: str) -> int:
        return ord(char) - cls.BASE_ELEVATION

    @classmethod
    def _load_line(cls, line: str, y: int, map: Dict[Position, int]) -> Tuple[Optional[Position], Optional[Position]]:
        found_st = None
        found_dest = None
        for x, character in enumerate(line):
            current = Position(x, y)
            if character == cls.START_CHAR:
                map[current] = cls.elevation('a')
                found_st = current
            elif character == cls.DEST_CHAR:
                map[current] = cls.elevation('z')
                found_dest = current
            else:
                map[current] = cls.elevation(character.lower())
        return found_st, found_dest

    @classmethod
    def from_file(cls, filename: str):
        map = {}
        start = None
        end = None
        print(f'Loading {filename}')
        with open(filename, 'r') as f:
            for y, line in enumerate(f):
                content = line.replace('\n', '')
                potential_start, potential_end = cls._load_line(content, -y, map)
                if potential_start is not None:
                    start = potential_start
                if potential_end is not None:
                    end = potential_end
        # to make (0,0) in the bottom left corner
        loading_offset = Position(0, y)
        return cls(
            elevation_map={
                # offset to start at 0
                pos + loading_offset: elevation
                for pos, elevation in map.items()
            },
            start=start + loading_offset,
            end=end + loading_offset,
        )


def q2_brute(map: Map):
    # I'm too lazy to refactor so we can do a single search from END to S (but with the rule of only going down by 1)
    # so that the complexity is reduced to 1 graph instead N graph resolutions
    start_positions = [
        position
        for position, elevation in map.elevation_map.items()
        if elevation == Map.elevation('a')
    ]
    best_route = None
    print(f'Found {len(start_positions)} start positions')
    for i, st in enumerate(start_positions, start=1):
        print(f'Computing {i}/{len(start_positions)}')
        candidate = map.shorted_path(st)
        if not candidate:
            print(f'  the route from {st} is empty!')
            continue
        if best_route is None or len(candidate) < len(best_route):
            print(f'  new best route is from {st}: {len(candidate) - 1} steps')
            best_route = candidate

    return best_route


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()

    elevation = Map.from_file(args.input)
    shortest = elevation.shorted_path()
    print(f'Q1: number of steps to target: {len(shortest) - 1}')
    if args.verbose:
        print(f'{", ".join(map(str, shortest))}')

    hiking = q2_brute(elevation)
    print(f'Q2: best hiking route is {len(hiking) - 1} steps')
