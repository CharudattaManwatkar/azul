from __future__ import annotations
from collections import Counter

from game_objects import Container, Brick, FactorySpace, FloorSpace,\
    PatternLine, CenterSpace



class TileTransferSpec:
    def __init__(
        self,
        src: Container,
        dest: Container,
        tile_counter: Counter,
    ) -> None:
        self.src = src
        self.dest = dest
        self.tile_counter = tile_counter


class TileTransfer:
    def __init__(
        self,
        src: Container,
        dest: Container,
        tile_counter: Counter,
        fulfilled: bool = False
        ) -> None:
        self.src = src
        self.dest = dest
        self.tile_counter = tile_counter
        self.fulfilled = fulfilled

    def is_valid_removal(self) -> bool:
        if isinstance(self.src, Brick):
            return False
        if self.src.yields_single_color:
            # Only 1 color should be requested to be removed
            if len(self.tile_counter) > 1:
                return False
            color = next(self.tile_counter.elements())
            # All tiles of the requested color should be removed
            if self.tile_counter.total() != self.tile_counter[color]:
                return False
        # Source must have adequeate tiles of all colors
        for color in self.tile_counter:
            request_count = self.tile_counter[color]
            src_count = self.src.tile_counter[color]
            if request_count > src_count:
                return False
        return True
        
    def is_valid_addition(self) -> bool:
        if not self.dest.allows_overflow:
            # Destination should have space to accomodate new tiles
            space_remaining = self.dest.size - self.dest.tile_counter.total()
            if space_remaining < 0:
                raise ValueError
            if self.tile_counter.total() > space_remaining:
                return False

        if self.dest.takes_single_color:
            # Only 1 color should be requested to be added
            if len(self.tile_counter) > 1:
                return False
            # If destination has some tiles, then only simliar colored tiles
            # should be added
            request_color = next(self.tile_counter.elements())
            if self.dest.tile_counter.total():    
                dest_color = next(self.dest.tile_counter.elements())
                if dest_color != request_color:
                    return False
    
            if isinstance(self.dest, Brick):
                dest_color = self.dest.color
                if dest_color != request_color:
                    return False

            if isinstance(self.dest, PatternLine):
                corresponding_brick: Brick = self.dest.bricks[request_color]
                if corresponding_brick.tile_counter.total():
                    return False

        return True

    def trigger_new_transfer(self) -> list[TileTransferSpec]:
        transfer_specs = []
        if isinstance(self.src, FactorySpace):
            deficit = self.src.size - self.src.tile_counter.total()
            if deficit:
                transfer_specs.append(
                    TileTransferSpec(
                        src=self.src,
                        dest=CenterSpace,
                        tile_counter=self.src.tile_counter
                    )
                )
        if isinstance(self.dest, PatternLine):
            excess = self.dest.tile_counter.total() - self.dest.size
            if excess:
                color = next(self.tile_counter.elements)
                transfer_specs.append(
                    TileTransferSpec(
                        src=self.dest,
                        dest=FloorSpace,
                        tile_counter=Counter({color: excess})
                    )
                )
        return transfer_specs

    def is_valid_transfer(self) -> bool:
        if not self.is_valid_removal():
            return False
        if not self.is_valid_addition():
            return False
        return True

    def execute(self) -> list[TileTransferSpec] | None:
        if not self.is_valid_transfer():
            raise Exception("Invalid Transfer Request")

        if self.fulfilled:
            return None

        self.src.tile_counter -= self.tile_counter
        self.dest.tile_counter += self.tile_counter
        self.fulfilled = True

        return self.trigger_new_transfer()
