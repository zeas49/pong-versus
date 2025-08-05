import pygame
import sys
import random
from player import HumanPlayer, AIPlayer
from ball import Ball
from scoreboard import Scoreboard
from sound_manager import SoundManager
from star_particles import StarParticleSystem

# Game constants
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_WIDTH = 10
PLAYER_HEIGHT = 130
BALL_SIZE = 30
PLAYER_OFFSET = 100

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pygame Pong")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = "TITLE"
        
        # Initialize game objects
        self.player1 = HumanPlayer(PLAYER_OFFSET, SCREEN_HEIGHT // 2, PLAYER_WIDTH, PLAYER_HEIGHT, WHITE, SCREEN_HEIGHT, SCREEN_WIDTH)
        self.player2 = AIPlayer(SCREEN_WIDTH - PLAYER_OFFSET, SCREEN_HEIGHT // 2, PLAYER_WIDTH, PLAYER_HEIGHT, WHITE, SCREEN_HEIGHT, SCREEN_WIDTH)
        self.ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, BALL_SIZE, WHITE, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.scoreboard = Scoreboard(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.sound_manager = SoundManager()
        self.star_particles = StarParticleSystem(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Gradient colors and direction
        self.gradient_color_base = (0, 0, 20) # Dark blue
        self.gradient_direction = 1 # 1 for normal, -1 for inverted
        self.gradient_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.update_gradient_surface()

        # Game sprites
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player1, self.player2, self.ball)
        
        # Input handling
        self.keys_pressed = set()

    def title_screen(self):
        title_font = pygame.font.Font(None, 74)
        button_font = pygame.font.Font(None, 50)
        instruction_font = pygame.font.Font(None, 30)

        title_text = title_font.render("Pygame Pong", True, WHITE)
        play_button_text = button_font.render("Play", True, BLACK)
        instructions = [
            "Controls:",
            "Mouse Y - Move Player 1",
            "Shift - Dash (direction based on mouse Y)",
            "Hold A - Charge",
            "Click Play to start!"
        ]

        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        play_button_rect = pygame.Rect(0, 0, 200, 70)
        play_button_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        while self.game_state == "TITLE":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.game_state = "EXIT"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button_rect.collidepoint(event.pos):
                        self.game_state = "PLAYING"

            self.screen.fill(BLACK)
            self.screen.blit(title_text, title_rect)
            pygame.draw.rect(self.screen, WHITE, play_button_rect)
            self.screen.blit(play_button_text, play_button_rect.center - pygame.Vector2(play_button_text.get_width() // 2, play_button_text.get_height() // 2))

            # Draw instructions
            for i, instruction in enumerate(instructions):
                inst_text = instruction_font.render(instruction, True, WHITE)
                inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120 + i * 30))
                self.screen.blit(inst_text, inst_rect)

            pygame.display.flip()
            self.clock.tick(60)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        mouse_y = pygame.mouse.get_pos()[1]
        self.player1.update(mouse_y) # Update player1 based on mouse position
        
        # Player 1 dash control with Shift key
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            if pygame.K_LSHIFT not in self.keys_pressed and pygame.K_RSHIFT not in self.keys_pressed:
                # Determine dash direction based on mouse position
                if mouse_y < SCREEN_HEIGHT // 2:
                    self.player1.start_dash(-1) # Dash up
                else:
                    self.player1.start_dash(1) # Dash down
                self.keys_pressed.add(pygame.K_LSHIFT) # Add one of them to avoid re-trigger
                self.keys_pressed.add(pygame.K_RSHIFT)
        else:
            if pygame.K_LSHIFT in self.keys_pressed or pygame.K_RSHIFT in self.keys_pressed:
                self.keys_pressed.discard(pygame.K_LSHIFT)
                self.keys_pressed.discard(pygame.K_RSHIFT)

        if keys[pygame.K_a]:
            if pygame.K_a not in self.keys_pressed:
                self.player1.start_charge()
                self.sound_manager.play_sound("charge")
                self.keys_pressed.add(pygame.K_a)
        else:
            if pygame.K_a in self.keys_pressed:
                self.player1.stop_charge()
                self.keys_pressed.remove(pygame.K_a)

    def check_collisions(self):
        # Ball collision with players
        if self.ball.rect.colliderect(self.player1.rect) and self.ball.dx < 0:
            # Calculate impact point
            impact_point = (self.ball.rect.centery - self.player1.rect.centery) / (PLAYER_HEIGHT / 2)
            
            self.ball.reverse_x()
            
            # Special effects for dash/charge
            if self.player1.dash_active:
                self.ball.dy += self.player1.dash_direction * 3 + impact_point * 1.5
                self.ball.dx *= 1.3
                self.sound_manager.play_sound("charge")
            elif self.player1.charge_active:
                charge_boost = self.player1.charge_level / self.player1.max_charge * 5
                self.ball.dx *= (1 + charge_boost * abs(impact_point))
                self.ball.dy += impact_point * charge_boost * 2
                self.sound_manager.play_sound("charge")
                self.player1.charge_level = 0
                self.player1.image.fill(WHITE)
            else:
                self.ball.dy += impact_point * 1.0
                
            self.sound_manager.play_sound("hit")
            self.gradient_direction *= -1 # Toggle gradient direction
            self.gradient_color_base = (random.randint(0, 50), random.randint(0, 50), random.randint(0, 50)) # New random dark color
            self.update_gradient_surface() # Update the pre-rendered gradient surface
            
        elif self.ball.rect.colliderect(self.player2.rect) and self.ball.dx > 0:
            # Calculate impact point
            impact_point = (self.ball.rect.centery - self.player2.rect.centery) / (PLAYER_HEIGHT / 2)
            
            self.ball.reverse_x()
            
            # AI dash effects
            if self.player2.dash_active:
                self.ball.dy += self.player2.dash_direction * 2.5 + impact_point * 1.2
                self.ball.dx *= 1.2
                self.sound_manager.play_sound("charge")
            else:
                self.ball.dy += impact_point * 0.8
                
            self.sound_manager.play_sound("hit")
            self.gradient_direction *= -1 # Toggle gradient direction
            self.gradient_color_base = (random.randint(0, 50), random.randint(0, 50), random.randint(0, 50)) # New random dark color
            self.update_gradient_surface() # Update the pre-rendered gradient surface

    def check_scoring(self):
        # Player 1 scores
        if self.ball.rect.centerx > SCREEN_WIDTH:
            self.scoreboard.update_score(1)
            self.ball.reset(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, -1)
            self.player1.rect.center = (PLAYER_OFFSET, SCREEN_HEIGHT // 2)
            self.player2.rect.center = (SCREEN_WIDTH - PLAYER_OFFSET, SCREEN_HEIGHT // 2)
            self.sound_manager.play_sound("point")
            
        # Player 2 scores
        elif self.ball.rect.centerx < 0:
            self.scoreboard.update_score(2)
            self.ball.reset(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 1)
            self.player1.rect.center = (PLAYER_OFFSET, SCREEN_HEIGHT // 2)
            self.player2.rect.center = (SCREEN_WIDTH - PLAYER_OFFSET, SCREEN_HEIGHT // 2)
            self.sound_manager.play_sound("point")

    def draw_center_line(self):
        # Draw center dividers
        for i in range(6):
            y_pos = i * 100 + 50
            pygame.draw.rect(self.screen, WHITE, (SCREEN_WIDTH // 2 - 2, y_pos, 4, 60))
            if y_pos + 100 < SCREEN_HEIGHT:
                pygame.draw.rect(self.screen, WHITE, (SCREEN_WIDTH // 2 - 2, y_pos + 100, 4, 60))

    def draw_gradient_background(self):
        # Vertical        self.gradient_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.update_gradient_surface()

    def update_gradient_surface(self):
        for y in range(SCREEN_HEIGHT):
            if self.gradient_direction == 1:
                r_v = int(self.gradient_color_base[0] * (y / SCREEN_HEIGHT))
                g_v = int(self.gradient_color_base[1] * (y / SCREEN_HEIGHT))
                b_v = int(self.gradient_color_base[2] * (y / SCREEN_HEIGHT))
            else:
                r_v = int(self.gradient_color_base[0] * (1 - y / SCREEN_HEIGHT))
                g_v = int(self.gradient_color_base[1] * (1 - y / SCREEN_HEIGHT))
                b_v = int(self.gradient_color_base[2] * (1 - y / SCREEN_HEIGHT))
            color_v = (r_v, g_v, b_v)
            pygame.draw.line(self.gradient_surface, color_v, (0, y), (SCREEN_WIDTH, y))

        for x in range(SCREEN_WIDTH):
            if self.gradient_direction == 1:
                r_h = int(self.gradient_color_base[0] * (x / SCREEN_WIDTH))
                g_h = int(self.gradient_color_base[1] * (x / SCREEN_WIDTH))
                b_h = int(self.gradient_color_base[2] * (x / SCREEN_WIDTH))
            else:
                r_h = int(self.gradient_color_base[0] * (1 - x / SCREEN_WIDTH))
                g_h = int(self.gradient_color_base[1] * (1 - x / SCREEN_WIDTH))
                b_h = int(self.gradient_color_base[2] * (1 - x / SCREEN_WIDTH))
            color_h = (r_h, g_h, b_h)
            pygame.draw.line(self.gradient_surface, color_h, (x, 0), (x, SCREEN_HEIGHT))

    def draw_gradient_background(self):
        self.screen.blit(self.gradient_surface, (0, 0))

    def game_loop(self):
        while self.game_state == "PLAYING":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.game_state = "EXIT"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = "TITLE"

            self.handle_input()
            
            # Update game objects
            # self.player1.update() # Player 1 movement is now handled by mouse in handle_input
            self.player2.update(self.ball.rect.centerx, self.ball.rect.centery)
            self.ball.update()
            self.star_particles.update()
            
            # Check collisions and scoring
            self.check_collisions()
            self.check_scoring()
            
            # Draw everything
            self.draw_gradient_background()
            self.star_particles.draw(self.screen)
            self.draw_center_line()
            self.ball.draw_wind_trail(self.screen)
            self.all_sprites.draw(self.screen)
            self.scoreboard.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(60)

    def run(self):
        while self.running:
            if self.game_state == "TITLE":
                self.title_screen()
            elif self.game_state == "PLAYING":
                self.game_loop()
            elif self.game_state == "EXIT":
                self.running = False

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()