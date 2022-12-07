import abc
import dataclasses
import re
from argparse import ArgumentParser
from operator import attrgetter
from typing import (
    ClassVar,
    Dict,
    Iterable,
    List,
    Optional,
    Self,
    Union,
)


def format_size(size: int, iso=False) -> str:
    if iso:
        mult = 1024.0
    else:
        mult = 1000.0
    unit_idx = -1
    units = ('k', 'M', 'G', 'T', 'P')

    current_size = float(size)
    while current_size >= mult and unit_idx + 1 < len(units):
        current_size = current_size / mult
        unit_idx += 1

    if unit_idx == -1:
        return f'{size}B'
    unit = units[unit_idx]
    if iso:
        unit = unit.upper() + 'i'
    return f'{current_size:.2f}{unit}B'


@dataclasses.dataclass
class BaseFile(metaclass=abc.ABCMeta):
    ROOT_NAME: ClassVar[str] = '/'

    name: str
    parent: Optional[Self] = None

    @property
    def full_path(self) -> str:
        full_path = [self.name]
        current = self.parent
        while current is not None:
            if current.name != self.ROOT_NAME:
                full_path.append(current.name)
            current = current.parent
        return '/'.join(reversed(full_path))

    @property
    @abc.abstractmethod
    def size(self) -> int:
        ...

    def human_size(self) -> str:
        return format_size(self.size)

    @property
    def is_dir(self) -> bool:
        return isinstance(self, Dir)


@dataclasses.dataclass
class File(BaseFile):
    _size: int = 0

    @property
    def size(self) -> int:
        return self._size


@dataclasses.dataclass
class Dir(BaseFile):
    PARENT_NAME: ClassVar[str] = '..'

    # files or dir
    files: List[File] = dataclasses.field(default_factory=list)
    sub_dirs: Dict[str, Self] = dataclasses.field(default_factory=dict)

    @property
    def size(self) -> int:
        return sum((f.size for f in self.files + list(self.sub_dirs.values())))

    @property
    def has_subdirs(self) -> bool:
        return bool(self.sub_dirs)

    def add(self, other: Union[File, Self]):
        if other.is_dir:
            self.sub_dirs[other.name] = other
        else:
            self.files.append(other)

    def change_dir(self, target: str) -> Optional[Self]:
        if target == self.PARENT_NAME:
            return self.parent
        return self.sub_dirs.get(target)

    def load_list(self, commands: List[str]) -> List[str]:
        dir_line = re.compile(r'^dir (.+)')
        file_line = re.compile(r'^(\d+) (.+)')
        while commands and not commands[0].startswith('$'):
            line = commands.pop(0)

            is_dir = dir_line.match(line)
            if is_dir is not None:
                dir_name = is_dir.group(1)
                if dir_name in (self.ROOT_NAME, self.PARENT_NAME):
                    raise RuntimeError('Cannot add a reserved name')
                self.add(Dir(dir_name, parent=self))
                continue

            is_file = file_line.match(line)
            if is_file is not None:
                self.add(File(is_file.group(2), _size=int(is_file.group(1)), parent=self))
                continue

            raise RuntimeError(f'Unexpected ls line: {line}')

        return commands

    def search_subdirs(self, max_size: int = None, min_size: int = None) -> Iterable[Self]:
        for dir in self.sub_dirs.values():
            if max_size is not None and dir.size < max_size:
                yield dir
            elif min_size is not None and dir.size >= min_size:
                yield dir
            yield from dir.search_subdirs(max_size=max_size, min_size=min_size)

    @classmethod
    def create_tree(cls, lines: Iterable[str]) -> Self:
        commands = list(lines)  # copy so we can pop without changing the input
        root = Dir(name=cls.ROOT_NAME)
        current_dir: Optional[Dir] = None

        cd_cmd = re.compile(r'^\$ cd (.+)')
        ls_cmd = re.compile(r'^\$ ls')

        while commands:
            line = commands.pop(0)
            is_cd = cd_cmd.match(line)
            if is_cd is not None:
                target = is_cd.group(1)
                if target == root.name:
                    current_dir = root
                elif current_dir is not None:
                    current_dir = current_dir.change_dir(target)
                else:
                    raise RuntimeError('No current dir')
                continue

            if ls_cmd.match(line) is not None:
                if current_dir is None:
                    raise RuntimeError('No current dir')
                commands = current_dir.load_list(commands)
                continue

            raise RuntimeError(f'Unexpected line: {line}')

        return root

    @classmethod
    def load_from_script(cls, filename: str) -> Self:
        # TODO(tr) Make the create_tree work without having to load the whole file in memory?
        #  maybe command by command?
        #  or line by line to work a bit like a pipe?
        print(f'Loading {filename}')
        with open(filename, 'r') as f:
            lines = [
                line.replace('\n', '')
                for line in f
            ]
        return cls.create_tree(lines)


def compute_q1(from_dir: Dir, max_size=100000, verbose=False) -> int:
    total = 0
    print(f'Looking for dir.size < {format_size(max_size)}')
    i = 0
    for i, dir in enumerate(from_dir.search_subdirs(max_size), start=1):
        if verbose:
            print(f'Found {dir.full_path}: {dir.human_size()}')
        total += dir.size
    print(f'Found {i} dirs')
    return total


def compute_q2(from_dir: Dir, desired_size=30000000, fs_size=70000000, verbose=False) -> int:
    usage = from_dir.size
    print(f'Current usage is {usage} ({format_size(usage)}): {usage/fs_size * 100.0:.2f}% of {format_size(fs_size)}')
    current_free = fs_size - usage
    if current_free >= desired_size:
        print('Desired space reached without deletion')
        return 0
    target = desired_size - current_free
    print(
        f'Need to free {target} ({format_size(target)}) to reach {format_size(desired_size)} free space '
        f'({desired_size / fs_size * 100.0:.2f}%)',
    )

    candidates: List[Dir] = sorted(from_dir.search_subdirs(min_size=target), key=attrgetter('size'))
    if not candidates:
        print('Found no single dir to reach that target')
        return 0
    selected = candidates[0]
    print(f'Found {len(candidates)} dirs')
    if verbose:
        for c in reversed(candidates[1:]):
            print(f'Found {c.full_path}: {c.human_size()}')

    print(f'Selected {selected.full_path}: {selected.human_size()}')
    return selected.size


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    parser.add_argument('--q2-fs-size', type=int, default=70000000, help='Q2: Total file system size')
    parser.add_argument('--q2-target', type=int, default=30000000, help='Q2: Target to free')
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    args = parser.parse_args()

    root = Dir.load_from_script(args.input)

    q1 = compute_q1(root, verbose=args.verbose)
    print(f'Q1: total size: {q1} (human: {format_size(q1)})')

    q2 = compute_q2(root, args.q2_target, args.q2_fs_size, verbose=args.verbose)
    print(f'Q2: total to save: {q2}')
