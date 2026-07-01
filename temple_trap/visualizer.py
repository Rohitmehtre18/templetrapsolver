import os
import pygame
import sys
from .config import COLS

# Maps the characters straight to your image assets A-H
SYMBOL_TO_LETTER = {
    "=": "A",
    "◻": "B",
    "+": "C",
    "◊": "D",
    "∗": "E",
    "▷": "F",
    "X": "G",
    "O": "H",
    " ": "BLANK"
}

CELL_SIZE = 160
WINDOW_SIZE = (COLS * CELL_SIZE, 3 * CELL_SIZE)
FPS = 60

class GameVisualizer:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Temple Trap Solver Visualizer")
        self.clock = pygame.time.Clock()
        self.assets = {}
        self.load_assets()

    def load_assets(self):
        assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
        for letter in ["A", "B", "C", "D", "E", "F", "G", "H"]:
            img_path = os.path.join(assets_dir, f"tile_{letter}.png")
            if os.path.exists(img_path):
                img = pygame.image.load(img_path).convert_alpha()
                self.assets[letter] = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
            else:
                surf = pygame.Surface((CELL_SIZE, CELL_SIZE))
                surf.fill((180, 160, 130))
                pygame.draw.rect(surf, (0, 0, 0), surf.get_rect(), 2)
                self.assets[letter] = surf

    def draw_state(self, gs):
        self.screen.fill((25, 35, 45))
        for idx, tile_symbol in enumerate(gs.tiles):
            if tile_symbol == " ": continue
            r, c = divmod(idx, COLS)
            x, y = c * CELL_SIZE, r * CELL_SIZE

            letter = SYMBOL_TO_LETTER[tile_symbol]
            base_img = self.assets[letter]

            # In final.py, orientations are stored as counter-clockwise rotational factors (0=0, 1=90, 2=180, 3=270)
            rot_deg = -gs.rotations[idx] * 90
            rotated_img = pygame.transform.rotate(base_img, rot_deg)
            new_rect = rotated_img.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
            self.screen.blit(rotated_img, new_rect.topleft)

        # Draw Pawn Avatar Core
        pawn_r, pawn_c = divmod(gs.pawn, COLS)
        px = pawn_c * CELL_SIZE + CELL_SIZE // 2
        py = pawn_r * CELL_SIZE + CELL_SIZE // 2
        pawn_color = (240, 60, 60) if gs.layer == "Ground" else (245, 215, 45)
        
        pygame.draw.circle(self.screen, pawn_color, (px, py), 22)
        pygame.draw.circle(self.screen, (255, 255, 255), (px, py), 22, 3)
        pygame.display.flip()

    def play_solution(self, initial_state, solution_path):
        current_state = initial_state
        step_idx = 0
        self.draw_state(current_state)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_SPACE, pygame.K_RIGHT]:
                        if step_idx < len(solution_path):
                            action, arg = solution_path[step_idx]
                            if action == "slide":
                                current_state.slide(arg)
                            elif action == "walk":
                                dest_idx, dest_layer, _ = arg
                                current_state.pawn = dest_idx
                                current_state.layer = dest_layer
                            step_idx += 1
                            self.draw_state(current_state)
                        else:
                            print("🏁 Target reached!")
            self.clock.tick(FPS)