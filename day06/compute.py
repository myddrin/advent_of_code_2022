import dataclasses
from argparse import ArgumentParser
from typing import (
    ClassVar,
    Optional,
    Self,
    Tuple,
)


PacketInfo = Tuple[int, Optional[str]]


@dataclasses.dataclass
class Message:
    START_OF_PACKET_LEN: ClassVar = 4
    START_OF_MSG_LEN: ClassVar = 14

    content: str

    def find_start(self, length: int, start: int = None) -> PacketInfo:
        if start is None:
            start = length
        for i in range(start, len(self.content)):
            packet = self.content[i - length:i]
            # First packet that has 4 unique characters
            if len(packet) == len(set(packet)):
                return i, packet
        return -1, None

    def find_start_of_packet(self) -> PacketInfo:
        return self.find_start(self.START_OF_PACKET_LEN)

    def find_start_of_message(self):
        return self.find_start(self.START_OF_MSG_LEN)

    @classmethod
    def from_file(cls, filename: str) -> Self:
        content = ''
        with open(filename, 'r') as f:
            for line in f:
                content += line.replace('\n', '')
        return cls(content)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='Input file')
    args = parser.parse_args()

    message = Message.from_file(args.input)

    offset, packet = message.find_start_of_packet()
    print(f'Q1: start of packets offset: {offset} {packet}')

    offset, _ = message.find_start_of_message()
    print(f'Q2: start of message offset: {offset}')
