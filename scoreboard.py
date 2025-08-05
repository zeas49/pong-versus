import pygame

class Scoreboard:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.score_a = 0
        self.score_b = 0
        self.font = pygame.font.Font(None, 250) # Much larger font
        self.alpha_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)

    def update_score(self, player):
        if player == 1:
            self.score_a += 1
        elif player == 2:
            self.score_b += 1

    def draw(self, screen):
        # Clear previous drawing on the alpha surface
        self.alpha_surface.fill((0, 0, 0, 0))

        score_text = self.font.render(f"{self.score_a}    {self.score_b}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        
        # Draw the score text onto the alpha surface with transparency
        self.alpha_surface.blit(score_text, score_rect)
        self.alpha_surface.set_alpha(50) # Set transparency (0-255, 50 is quite opaque)

        # Blit the alpha surface onto the main screen
        screen.blit(self.alpha_surface, (0, 0))

    def reset(self):
        self.score_a = 0
        self.score_b = 0


