# from typing import Union, List, Set
from __future__ import annotations
from enum import Enum
from random import shuffle
from collections import Counter
from abc import ABC, abstractmethod


class TileColor(Enum):
    BLUE = 1
    YELLOW = 2
    RED = 3
    BLACK = 4
    TEAL = 5

    def __str__(self):
        return self.name

    def __repr__(self) -> str:
        return f"TileColor({self.name})"


# class Tile:
#     def __init__(self, color: TileColor) -> None:
#         self.color = color
#         # TODO: Maybe add a location attribute

#     def __str__(self) -> str:
#         return f"{str(self.color)} Tile"

#     def __repr__(self) -> str:
#         return f"Tile({self.color})"


class Container(ABC):
    def __init__(self, size: int, allows_overflow: bool = False,
                 yields_single_color: bool = False,
                 takes_single_color: bool = False) -> None:
        self.size = size
        self.allows_overflow = allows_overflow
        self.yields_single_color = yields_single_color
        self.takes_single_color = takes_single_color
        self.tile_counter = Counter({c: 0 for c in TileColor})

    @abstractmethod
    def can_send_tiles_to(self, container: Container) -> bool:
        pass

    def is_empty(self) -> bool:
        return self.tile_counter.total() == 0

    


class Bag(Container):
    def __init__(self):
        super().__init__(size=100)
        self.tile_counter = Counter({c:20 for c in TileColor})
    
    def can_send_tiles_to(self, container: Container) -> bool:
        return isinstance(container, FactorySpace)


class FactorySpace(Container):
    def __init__(self):
        super().__init__(size=4, yields_single_color=True)

    def can_send_tiles_to(self, container: Container) -> bool:
        return isinstance(container, (CenterSpace, PatternLine))


class CenterSpace(Container):
    def __init__(self):
        super().__init__(size=100, yields_single_color=True)

    def can_send_tiles_to(self, container: Container) -> bool:
        return isinstance(container, PatternLine)


class Brick(Container):
    def __init__(self, row, column):
        super().__init__(
            size=1,
            takes_single_color=True,
            allows_overflow=False
            )
        self.row = row
        self.column = column
        self.color = TileColor(1 + (column - row) % 5)
    
    def can_send_tiles_to(self, container: Container) -> bool:
        return False


class PatternLine(Container):
    def __init__(self, size: int | None) -> None:
        super().__init__(size, allows_overflow=True, takes_single_color=True)
        self.row = size
        # Populate after instantiating all the bricks
        self.bricks = {TileColor(i+1): None for i in range(4)}

    def can_send_tiles_to(self, container: Container) -> bool:
        return isinstance(container, (Brick, Bag, FloorSpace))
    
    def get_color(self):
        if self.tile_counter.total():
            raise Exception("More than 1 color found in Pattern Line")
        return self.tile_counter.keys()[0]


class FloorSpace(Container):
    def __init__(self, idx: int) -> None:
        super().__init__(
            size=1,
            allows_overflow=False,
            yields_single_color=True,
            takes_single_color=True
            )
        self.idx: int = idx
        self.penalty: int = self.get_penalty(idx)

    def get_penalty(idx) -> int:
        if idx < 0:
            raise ValueError
        if idx < 2:
            return 1
        if idx < 5:
            return 2
        return 3


class Board:
    def __init__(self) -> None:
        self.pattern_lines: list[PatternLine] = [
            PatternLine(size=i) for i in range(1, 6)
        ]
        self.floor: list[FloorSpace] = [FloorSpace(idx=i) for i in range(20)]
        self.wall: dict[int, dict[int, Brick]] = {
            i: {j: Brick(i, j)} for i in range(6) for j in range(6)
        }
        self.connect_lines_to_bricks()
    
    def connect_lines_to_bricks(self) -> None:
        for i, pattern_line in enumerate(self.pattern_lines):
            bricks = self.wall[i].values()
            pattern_line.bricks = {b.color: b for b in bricks}

    @property
    def tile_counter(self):
        _tile_counter: Counter = Counter({c: 0 for c in TileColor})
        for line in self.pattern_lines:
            _tile_counter += line.tile_counter
        for floorspace in self.floor:
            _tile_counter += floorspace.tile_counter
        for i in range(6):
            for j in range(6):
                _tile_counter += self.wall[i][j].tile_counter
        return _tile_counter

    # TO DO : Forbid modifying the Board tile counter directly

