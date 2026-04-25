# viewer_pygame.py
import sys
import pygame
from .automata import (
    CombatSimulation, Cell
)
from gridcore.simulation import Snapshot

CELL_PX  = 20
PHASE_MS = 10
BG_COLOR = (30,30,30)
PLAYER_COLORS = {
    1:       (  0,200,  0),   # faction 0
    2:       (200,  0,  0),   # faction 1
    3:       (  0,  0,200),   # faction 2
    4:       (  100,  200,100),   # faction 2
    5:       (  0,  100,200),   # faction 2
    6:       (  100,  100,0),   # faction 2
}

def draw(state: Snapshot, surface: pygame.Surface) -> None:
    board = state.board
    for x in range(board.width):
        for y in range(board.height):
            pygame.draw.rect(
                surface,
                COLOR[board.cells[x][y]],
                (x * CELL_PX, y * CELL_PX, CELL_PX - 1, CELL_PX - 1)
            )

def check_for_events() -> list[PlayerAction]:

    actions = []                               # collect during INPUT phase
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            actions.append(
                PlayerAction(ActionType.TOGGLE, mx // CELL_PX, my // CELL_PX)
            )

    return actions

def main() -> None:
    engine  = CombatSimulation(50, 50)
    gstate  = engine.snapshot()

    pygame.init()
    screen = pygame.display.set_mode(
        (gstate.width * CELL_PX, gstate.height * CELL_PX)
    )
    clock  = pygame.time.Clock()

    phase, phase_start = "input", pygame.time.get_ticks()
    running = True
    while running:
        now = pygame.time.get_ticks()
        if now - phase_start >= PHASE_MS:
            phase_start = now
            actions = check_for_events()
            gstate = engine.advance(actions)  # hand over ALL actions

            caption = (
                f"Game over: {gstate.outcome.upper()}"
                if gstate.outcome != "ongoing"
                else f"Phase: {phase}"
            )
            pygame.display.set_caption(caption)

            draw(gstate, screen)
            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    main()
