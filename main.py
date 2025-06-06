import pygame
import sys
from levels import get_level, total_levels
from game_state import GameState
import numpy as np

# Initialize Pygame
pygame.init()

# Constants
TILE_SIZE = 60  # Increased tile size for better visuals
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
BROWN = (139, 69, 19)
LIGHT_BROWN = (205, 133, 63)
GREEN = (34, 139, 34)
LIGHT_GREEN = (144, 238, 144)
BLUE = (30, 144, 255)
LIGHT_BLUE = (135, 206, 250)
RED = (220, 20, 60)
WALL_DARK = (90, 90, 90)
WALL_LIGHT = (180, 180, 180)
BOX_DARK = (120, 60, 20)
BOX_LIGHT = (210, 140, 80)
FLOOR_DARK = (40, 40, 40)
FLOOR_LIGHT = (60, 60, 60)
TARGET_DARK = (25, 100, 25)
TARGET_LIGHT = (50, 180, 50)
PLAYER_DARK = (20, 100, 180)
PLAYER_LIGHT = (100, 180, 255)

# Button dimensions
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 40
BUTTON_MARGIN = 10

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = pygame.font.Font(None, 32)

    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=5)
        
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            return False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Sokoban Puzzle")
        self.clock = pygame.time.Clock()
        self.game_state = GameState()
        self.moves = 0
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Create buttons
        button_x = WINDOW_WIDTH - BUTTON_WIDTH - BUTTON_MARGIN
        self.reset_button = Button(button_x, BUTTON_MARGIN, BUTTON_WIDTH, BUTTON_HEIGHT, 
                                 "Reset Level (R)", DARK_GRAY, GRAY)
        self.save_button = Button(button_x, 2 * BUTTON_MARGIN + BUTTON_HEIGHT, 
                                BUTTON_WIDTH, BUTTON_HEIGHT, "Save Game (Space)", DARK_GRAY, GRAY)
        self.menu_button = Button(button_x, 3 * BUTTON_MARGIN + 2 * BUTTON_HEIGHT, 
                                BUTTON_WIDTH, BUTTON_HEIGHT, "Level Select (Q)", DARK_GRAY, GRAY)
        
        self.in_level_select = False
        self.load_level(self.game_state.current_level)

    def load_level(self, level_number):
        level_data = get_level(level_number)
        if level_data is None:
            return False
        
        self.level = level_data
        self.moves = 0
        self.height = len(level_data)
        self.width = max(len(row) for row in level_data)
        
        # Convert level to numpy array for efficient manipulation
        self.board = np.full((self.height, self.width), ' ')
        self.targets = np.full((self.height, self.width), False)
        
        # Find player position and fill board
        self.player_pos = None
        for y, row in enumerate(level_data):
            for x, cell in enumerate(row):
                if cell == '@':
                    self.player_pos = (x, y)
                    self.board[y, x] = ' '
                elif cell == '+':
                    self.player_pos = (x, y)
                    self.board[y, x] = ' '
                    self.targets[y, x] = True
                elif cell == '.':
                    self.board[y, x] = ' '
                    self.targets[y, x] = True
                elif cell == '*':
                    self.board[y, x] = '$'
                    self.targets[y, x] = True
                else:
                    self.board[y, x] = cell
        
        return True

    def draw_level_select(self):
        self.screen.fill(BLACK)
        title = self.font.render("Level Select", True, WHITE)
        title_rect = title.get_rect(centerx=WINDOW_WIDTH//2, y=20)
        self.screen.blit(title, title_rect)

        # Calculate grid layout
        levels_per_row = 5
        button_width = 120
        button_height = 80
        margin = 20
        start_x = (WINDOW_WIDTH - (levels_per_row * (button_width + margin) - margin)) // 2
        start_y = 100

        # Get highest completed level
        highest_level = -1
        if self.game_state.scores:
            try:
                highest_level = max(int(k) for k in self.game_state.scores.keys())
            except ValueError:
                highest_level = -1

        for i in range(total_levels()):
            row = i // levels_per_row
            col = i % levels_per_row
            x = start_x + col * (button_width + margin)
            y = start_y + row * (button_height + margin)

            # Create button rectangle
            button_rect = pygame.Rect(x, y, button_width, button_height)
            # Make level available if it's within one level of the highest completed
            color = GRAY if i <= highest_level + 1 else DARK_GRAY
            pygame.draw.rect(self.screen, color, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, WHITE, button_rect, 2, border_radius=10)

            # Level number
            level_text = self.font.render(f"Level {i+1}", True, WHITE)
            level_rect = level_text.get_rect(centerx=button_rect.centerx, centery=button_rect.centery-10)
            self.screen.blit(level_text, level_rect)

            # Best score
            best_score = self.game_state.get_score(i)
            if best_score is not None:
                score_text = self.small_font.render(f"Best: {best_score}", True, LIGHT_GREEN)
                score_rect = score_text.get_rect(centerx=button_rect.centerx, centery=button_rect.centery+15)
                self.screen.blit(score_text, score_rect)

        # Add "Back" button at the bottom
        back_button_width = 200
        back_button_height = 40
        back_button_x = (WINDOW_WIDTH - back_button_width) // 2
        back_button_y = WINDOW_HEIGHT - back_button_height - 20
        back_button = pygame.Rect(back_button_x, back_button_y, back_button_width, back_button_height)
        
        # Draw back button with hover effect
        mouse_pos = pygame.mouse.get_pos()
        back_color = GRAY if back_button.collidepoint(mouse_pos) else DARK_GRAY
        pygame.draw.rect(self.screen, back_color, back_button, border_radius=5)
        pygame.draw.rect(self.screen, WHITE, back_button, 2, border_radius=5)
        
        back_text = self.font.render("Back (Esc)", True, WHITE)
        back_text_rect = back_text.get_rect(center=back_button.center)
        self.screen.blit(back_text, back_text_rect)

        pygame.display.flip()

    def draw_wall(self, x, y, width, height):
        """Draw a stylized wall tile with 3D effect."""
        # Main wall body
        pygame.draw.rect(self.screen, WALL_DARK, (x, y, width, height))
        
        # Top highlight
        pygame.draw.polygon(self.screen, WALL_LIGHT, [
            (x, y),
            (x + width, y),
            (x + width - 8, y + 8),
            (x + 8, y + 8)
        ])
        
        # Right highlight
        pygame.draw.polygon(self.screen, WALL_LIGHT, [
            (x + width, y),
            (x + width, y + height),
            (x + width - 8, y + height - 8),
            (x + width - 8, y + 8)
        ])
        
        # Bottom shadow
        pygame.draw.polygon(self.screen, DARK_GRAY, [
            (x, y + height),
            (x + width, y + height),
            (x + width - 8, y + height - 8),
            (x + 8, y + height - 8)
        ])

    def draw_box(self, x, y, width, height):
        """Draw a stylized box with wood-like texture."""
        # Main box body
        pygame.draw.rect(self.screen, BOX_DARK, (x, y, width, height))
        
        # Top highlight
        pygame.draw.polygon(self.screen, BOX_LIGHT, [
            (x, y),
            (x + width, y),
            (x + width - 6, y + 6),
            (x + 6, y + 6)
        ])
        
        # Right highlight
        pygame.draw.polygon(self.screen, BOX_LIGHT, [
            (x + width, y),
            (x + width, y + height),
            (x + width - 6, y + height - 6),
            (x + width - 6, y + 6)
        ])
        
        # Wood grain effect (horizontal lines)
        for i in range(3):
            y_pos = y + 15 + i * 15
            pygame.draw.line(self.screen, LIGHT_BROWN, 
                           (x + 10, y_pos), 
                           (x + width - 10, y_pos), 2)

    def draw_target(self, x, y, width, height):
        """Draw a stylized target spot with glowing effect."""
        # Outer glow
        glow_surf = pygame.Surface((width + 20, height + 20), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*TARGET_LIGHT, 100), 
                         (width//2 + 10, height//2 + 10), width//2 + 5)
        self.screen.blit(glow_surf, (x - 10, y - 10))
        
        # Main target
        pygame.draw.circle(self.screen, TARGET_DARK, 
                         (x + width//2, y + height//2), width//3)
        pygame.draw.circle(self.screen, TARGET_LIGHT, 
                         (x + width//2, y + height//2), width//3, 3)
        
        # Center dot
        pygame.draw.circle(self.screen, TARGET_LIGHT, 
                         (x + width//2, y + height//2), width//8)

    def draw_player(self, x, y, width, height):
        """Draw a stylized player character with animation."""
        # Calculate bounce offset for simple animation
        bounce_offset = abs(np.sin(pygame.time.get_ticks() * 0.005)) * 3
        
        # Shadow
        pygame.draw.ellipse(self.screen, DARK_GRAY,
                          (x + 5, y + height - 10, width - 10, 20))
        
        # Body
        pygame.draw.circle(self.screen, PLAYER_DARK,
                         (x + width//2, y + height//2 + bounce_offset),
                         width//2 - 5)
        
        # Highlight/Shine
        pygame.draw.circle(self.screen, PLAYER_LIGHT,
                         (x + width//2 - width//6, y + height//2 - height//6 + bounce_offset),
                         width//6)
        
        # Eyes
        eye_color = WHITE
        eye_size = width//8
        pygame.draw.circle(self.screen, eye_color,
                         (x + width//2 - eye_size, y + height//2 - eye_size + bounce_offset),
                         eye_size)
        pygame.draw.circle(self.screen, eye_color,
                         (x + width//2 + eye_size, y + height//2 - eye_size + bounce_offset),
                         eye_size)
        
        # Pupils
        pupil_color = BLACK
        pupil_size = eye_size//2
        pygame.draw.circle(self.screen, pupil_color,
                         (x + width//2 - eye_size, y + height//2 - eye_size + bounce_offset),
                         pupil_size)
        pygame.draw.circle(self.screen, pupil_color,
                         (x + width//2 + eye_size, y + height//2 - eye_size + bounce_offset),
                         pupil_size)

    def draw_floor(self, x, y, width, height):
        """Draw a stylized floor tile with subtle pattern."""
        pygame.draw.rect(self.screen, FLOOR_DARK, (x, y, width, height))
        
        # Subtle grid pattern
        pygame.draw.line(self.screen, FLOOR_LIGHT, 
                        (x, y), (x + width, y), 1)
        pygame.draw.line(self.screen, FLOOR_LIGHT, 
                        (x, y), (x, y + height), 1)

    def draw(self):
        if self.in_level_select:
            self.draw_level_select()
            return

        self.screen.fill(BLACK)
        
        # Calculate offset to center the level
        offset_x = (WINDOW_WIDTH - self.width * TILE_SIZE) // 2
        offset_y = (WINDOW_HEIGHT - self.height * TILE_SIZE) // 2
        
        # Draw board
        for y in range(self.height):
            for x in range(self.width):
                pos_x = offset_x + x * TILE_SIZE
                pos_y = offset_y + y * TILE_SIZE
                
                # Draw floor for all tiles
                self.draw_floor(pos_x, pos_y, TILE_SIZE, TILE_SIZE)
                
                # Draw target spots
                if self.targets[y, x]:
                    self.draw_target(pos_x, pos_y, TILE_SIZE, TILE_SIZE)
                
                # Draw walls
                if self.board[y, x] == '#':
                    self.draw_wall(pos_x, pos_y, TILE_SIZE, TILE_SIZE)
                
                # Draw boxes
                elif self.board[y, x] == '$':
                    self.draw_box(pos_x, pos_y, TILE_SIZE, TILE_SIZE)
        
        # Draw player
        if self.player_pos:
            player_x = offset_x + self.player_pos[0] * TILE_SIZE
            player_y = offset_y + self.player_pos[1] * TILE_SIZE
            self.draw_player(player_x, player_y, TILE_SIZE, TILE_SIZE)
        
        # Draw buttons
        self.reset_button.draw(self.screen)
        self.save_button.draw(self.screen)
        self.menu_button.draw(self.screen)
        
        # Draw level info
        level_text = self.font.render(f"Level: {self.game_state.current_level + 1}", True, WHITE)
        moves_text = self.font.render(f"Moves: {self.moves}", True, WHITE)
        best_score = self.game_state.get_score(self.game_state.current_level)
        best_text = self.font.render(f"Best: {best_score if best_score else 'N/A'}", True, WHITE)
        
        self.screen.blit(level_text, (10, 10))
        self.screen.blit(moves_text, (10, 50))
        self.screen.blit(best_text, (10, 90))
        
        pygame.display.flip()

    def move_player(self, dx, dy):
        new_x = self.player_pos[0] + dx
        new_y = self.player_pos[1] + dy
        
        # Check if move is within bounds
        if not (0 <= new_x < self.width and 0 <= new_y < self.height):
            return False
        
        # Check if moving into a wall
        if self.board[new_y, new_x] == '#':
            return False
        
        # Check if moving into a box
        if self.board[new_y, new_x] == '$':
            box_x = new_x + dx
            box_y = new_y + dy
            
            # Check if box can be pushed
            if not (0 <= box_x < self.width and 0 <= box_y < self.height):
                return False
            if self.board[box_y, box_x] in ['#', '$']:
                return False
            
            # Move box
            self.board[box_y, box_x] = '$'
            self.board[new_y, new_x] = ' '
        
        # Move player
        self.player_pos = (new_x, new_y)
        self.moves += 1
        return True

    def check_win(self):
        """Check if all boxes are on targets."""
        for y in range(self.height):
            for x in range(self.width):
                if self.targets[y, x] and self.board[y, x] != '$':
                    return False
        return True

    def handle_level_select_click(self, pos):
        levels_per_row = 5
        button_width = 120
        button_height = 80
        margin = 20
        start_x = (WINDOW_WIDTH - (levels_per_row * (button_width + margin) - margin)) // 2
        start_y = 100

        # Check for back button click
        back_button_width = 200
        back_button_height = 40
        back_button_x = (WINDOW_WIDTH - back_button_width) // 2
        back_button_y = WINDOW_HEIGHT - back_button_height - 20
        back_button = pygame.Rect(back_button_x, back_button_y, back_button_width, back_button_height)
        
        if back_button.collidepoint(pos):
            self.in_level_select = False
            return

        # Get highest completed level
        highest_level = -1
        if self.game_state.scores:
            try:
                highest_level = max(int(k) for k in self.game_state.scores.keys())
            except ValueError:
                highest_level = -1

        for i in range(total_levels()):
            row = i // levels_per_row
            col = i % levels_per_row
            x = start_x + col * (button_width + margin)
            y = start_y + row * (button_height + margin)
            
            button_rect = pygame.Rect(x, y, button_width, button_height)
            if button_rect.collidepoint(pos):
                # Only allow selecting levels that are within one level of the highest completed
                if i <= highest_level + 1:
                    self.game_state.set_level(i)
                    self.load_level(i)
                    self.in_level_select = False
                return

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.in_level_select:
                        self.handle_level_select_click(event.pos)
                    else:
                        if self.reset_button.handle_event(event):
                            self.load_level(self.game_state.current_level)
                        elif self.save_button.handle_event(event):
                            self.game_state.save_game()
                        elif self.menu_button.handle_event(event):
                            self.in_level_select = True
                
                elif event.type == pygame.MOUSEMOTION:
                    if not self.in_level_select:
                        self.reset_button.handle_event(event)
                        self.save_button.handle_event(event)
                        self.menu_button.handle_event(event)
                
                elif event.type == pygame.KEYDOWN:
                    if self.in_level_select:
                        if event.key == pygame.K_ESCAPE:
                            self.in_level_select = False
                    else:
                        moved = False
                        if event.key in [pygame.K_LEFT, pygame.K_a]:
                            moved = self.move_player(-1, 0)
                        elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                            moved = self.move_player(1, 0)
                        elif event.key in [pygame.K_UP, pygame.K_w]:
                            moved = self.move_player(0, -1)
                        elif event.key in [pygame.K_DOWN, pygame.K_s]:
                            moved = self.move_player(0, 1)
                        elif event.key == pygame.K_r:
                            self.load_level(self.game_state.current_level)
                        elif event.key == pygame.K_ESCAPE:
                            running = False
                        elif event.key == pygame.K_SPACE:
                            self.game_state.save_game()
                        elif event.key == pygame.K_q:
                            self.in_level_select = True
                        
                        if moved and self.check_win():
                            self.game_state.update_score(self.game_state.current_level, self.moves)
                            if self.game_state.current_level < total_levels() - 1:
                                self.game_state.advance_level()
                                self.load_level(self.game_state.current_level)
                            else:
                                print("Congratulations! You've completed all levels!")
                                running = False
            
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run() 