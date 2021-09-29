from abc import ABCMeta
from typing import Tuple

class Node(metaclass=ABCMeta):
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int]) -> None:
        self.start_pos = start
        self.end_pos = end

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self.start_pos[0]}:{self.start_pos[1]}>'

