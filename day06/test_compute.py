import os

import pytest

from .compute import Message


@pytest.fixture(scope='session')
def input_txt():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'input.txt',
    )


class TestMessage:

    @pytest.mark.parametrize('content, expected', (
        ('mjqjpqmgbljsphdztnvjfqwrcgsmlb', (7, 'jpqm')),
        ('bvwbjplbgvbhsrlpgdmjqwftvncz', (5, 'vwbj')),
        ('nppdvjthqldpwncqszvftbrmjlhg', (6, 'pdvj')),
        ('nznrnfrfntjfmvfwmzdfjlvtqnbhcprsg', (10, 'rfnt')),
        ('zcfzfwzzqfrljwzlrfnpqdbhtmscgvjw', (11, 'zqfr')),
    ))
    def test_find_start_of_packet(self, content, expected):
        assert Message(content).find_start_of_packet() == expected

    @pytest.mark.parametrize('content, expected_index', (
        ('mjqjpqmgbljsphdztnvjfqwrcgsmlb', 19),
        ('bvwbjplbgvbhsrlpgdmjqwftvncz', 23),
        ('nppdvjthqldpwncqszvftbrmjlhg', 23),
        ('nznrnfrfntjfmvfwmzdfjlvtqnbhcprsg', 29),
        ('zcfzfwzzqfrljwzlrfnpqdbhtmscgvjw', 26),
    ))
    def test_find_start_of_message(self, content, expected_index):
        assert Message(content).find_start_of_message()[0] == expected_index


class TestQuestions:

    def test_q1(self, input_txt):
        assert Message.from_file(input_txt).find_start_of_packet() == (1080, 'dcmv')

    def test_q2(self, input_txt):
        assert Message.from_file(input_txt).find_start_of_message()[0] == 3645
