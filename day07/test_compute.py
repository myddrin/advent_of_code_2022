import os

import pytest

from .compute import (
    Dir,
    compute_q1,
    compute_q2,
    format_size,
)


@pytest.fixture(scope='session')
def small_ex_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'small_ex.txt',
    )


@pytest.fixture(scope='session')
def small_ex(small_ex_txt):
    return Dir.load_from_script(small_ex_txt)


@pytest.fixture(scope='session')
def input_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'input.txt',
    )


@pytest.mark.parametrize('size, iso, human', (
    (800, False, '800B'),
    (1001, False, '1.00kB'),
    (1001, True, '1001B'),
    (1025, True, '1.00KiB'),
    (12014000, False, '12.01MB'),
    (12014000, True, '11.46MiB'),
    (130028930001, False, '130.03GB'),  # rounds up
    (130028930001, True, '121.10GiB'),  # rounds up
    (4013032020001, False, '4.01TB'),
    (4013032020001, True, '3.65TiB'),
    (5030040013020001, False, '5.03PB'),
    (5030040013020001, True, '4.47PiB'),
))
def test_format_size(size, iso, human):
    assert format_size(size, iso=iso) == human


class TestDir:

    @pytest.mark.parametrize('commands, left', (
        (
            ('dir a', '14848514 b.txt', '8504156 c.dat',),  # nothing else afterwards
            0,
        ),
        (
            ('dir a', '14848514 b.txt', '8504156 c.dat', '$ cd /'),  # stops before the end
            1,
        ),
    ))
    def test_load_ls(self, commands, left):
        root = Dir('/')

        commands = list(commands)
        new_commands = root.load_list(commands)

        assert new_commands is commands
        assert len(commands) == left, 'should have consumed it all'

        assert list(root.sub_dirs.keys()) == ['a']
        assert {
            f.name: f.size
            for f in root.files
        } == {
            'b.txt': 14848514,
            'c.dat': 8504156,
        }

    def test_load_small_ex(self, small_ex_txt):
        root = Dir.load_from_script(small_ex_txt)
        assert root.name == '/'
        assert root.size == 48381165
        assert root.has_subdirs is True

        a = root.change_dir('a')
        assert a.size == 94853
        assert a.has_subdirs is True

        e = a.change_dir('e')
        assert e.size == 584
        assert e.has_subdirs is False

        d = root.change_dir('d')
        assert d.size == 24933642
        assert d.has_subdirs is False

    def test_search_subdirs(self, small_ex):
        found = list(small_ex.search_subdirs(100000))

        assert len(found) == 2
        assert found[0].name == 'a'
        assert found[0].size == 94853
        assert found[1].name == 'e'
        assert found[1].size == 584


class TestQuestion1:

    def test_small_ex(self, small_ex):
        assert compute_q1(small_ex) == 95437

    def test_input(self, input_txt):
        assert compute_q1(Dir.load_from_script(input_txt)) == 1501149


class TestQuestion2:

    def test_small_ex(self, small_ex):
        assert compute_q2(small_ex) == 24933642

    def test_input(self, input_txt):
        assert compute_q2(Dir.load_from_script(input_txt)) == 10096985
