from abc import ABC, abstractmethod
from __future__ import annotations
from enum import Enum, auto
from random import shuffle, seed
from collections import Counter

from game_objects import Bag, Container, Brick, FactorySpace, FloorSpace,\
    PatternLine, CenterSpace, Board
from transfer import TileTransfer, TileTransferSpec

PLAYER_TO_FACTORY_COUNT = {1:4, 2:5, 3:6, 4: 7}
seed(42)


class Player(ABC):
    def __init__(self) -> None:
        self.board: Board = Board()
        self.score: int = 0
    
    @abstractmethod
    def attempt_to_play(self, game_state: GameState) -> TileTransfer:
        pass


class Bot(Player):
    def __init__(self) -> None:
        super().__init__()


class Human(Player):
    def __init__(self) -> None:
        super().__init__()



class Phase(Enum):
    DRAFT = auto()
    PLAY = auto()
    SCORE = auto()

    def next(self):
        transitions = {
            Phase.DRAFT: Phase.PLAY,
            Phase.PLAY: Phase.SCORE,
            Phase.SCORE: Phase.DRAFT 
        }
        return transitions.get(self)


# TO DO: Make this a singleton? Or maybe not
class GameState:
    def __init__(self) -> None:
        self.factories = [
            FactorySpace() for _ in range(
                PLAYER_TO_FACTORY_COUNT[len(self.players)]
            )
        ]
        self.center_space: CenterSpace = CenterSpace()
        self.bag: Bag = Bag()
        self.turn_idx: int = 0
        self.phase = Phase.DRAFT
    
    def is_last_round(self) -> bool:
        ...

    def is_game_over(self) -> bool:
        ...
    
    def is_phase_over(self) -> bool:
        ...

# Game manager:
    # Instantiate players
    # Track turn order
    # Initiate every container
    # Execute move requests from players
    # track scores

class GameManager:
    def __init__(self, n_humans: int, n_bots: int) -> None:
        self.bots: list[Bot] = [Bot() for _ in range(n_bots)]
        self.humans: list[Human] = [Human() for _ in range(n_humans)]
        self.players: dict[int, Player] = {
            idx: player for idx, player in shuffle(self.bots + self.humans)
        }
        self.game_state: GameState = GameState()
        self.game_paused: bool = False

    def run_game(self) -> None:
        while not self.game_state.is_game_over():
            phase = self.game_state.phase
            self.advance_phase(phase)

    def advance_phase(self, phase):
        if phase is Phase.DRAFT:
            self.advance_draft_phase()
        elif phase is Phase.PLAY:
            self.advance_play_phase()
        elif phase is Phase.SCORE:
            ...

    def advance_draft_phase(self):
        for f in self.game_state.factories:
            if not f.is_empty():
                raise Exception(
                    "All Factories needs to be empty before refilling"
                    )
            tile_counter = self.draw_four()
            tile_transfer = TileTransfer(
                src=self.game_state.bag, dest=f, tile_counter=tile_counter
                )
            result = tile_transfer.execute()
            if result is not None:
                raise Exception("Unexpected resultant transfer")

    def draw_four(self):
        ...

    def resolve_spec(self, transfer_spec: TileTransferSpec) -> TileTransfer:
        ...

    def resolve_or_execute_transfer(
        self, transfer: TileTransferSpec | TileTransfer | None
    ):
        if transfer is None:
            return
        if isinstance(transfer, TileTransferSpec):
            transfer = self.resolve_spec(transfer)
        return transfer.execute()


    def advance_play_phase(self):
        while not all(f.is_empty() for f in self.game_state.factories):
            p = self.players[self.game_state.turn_idx]
            transfer_request = p.attempt_to_play(self.game_state)
            result = transfer_request.execute()
            if result is None:
                continue
            if not isinstance(result, list) and not isinstance(result[0], TileTransferSpec):
                raise Exception(
                    f"Transfer Request execution must result in None or "\
                    f"List[TileTransferSpec] but got {result}"
                )
            for spec in result:
                resultant_request = self.resolve_spec(spec)
                resultant_request.execute()
            self.game_state.turn_idx = (self.game_state.turn_idx + 1) % len(self.players)



