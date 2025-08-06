import pygame

class CrosshairCursor(pygame.sprite.Sprite):
    def __init__(self, size=20, line_width=2, color=(255, 255, 255)):
        super().__init__()
        self.size = size
        self.line_width = line_width
        self.color = color
        self.image = pygame.Surface([size, size], pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.angle = 0
        self.rotation_speed = 3 # degrees per frame

    def draw_crosshair(self):
        self.image.fill((0, 0, 0, 0)) # Clear previous drawing
        half_size = self.size // 2

        # Draw four rectangles that converge
        # Top rectangle
        pygame.draw.rect(self.image, self.color, (half_size - self.line_width // 2, 0, self.line_width, half_size - self.line_width))
        # Bottom rectangle
        pygame.draw.rect(self.image, self.color, (half_size - self.line_width // 2, half_size + self.line_width, self.line_width, half_size - self.line_width))
        # Left rectangle
        pygame.draw.rect(self.image, self.color, (0, half_size - self.line_width // 2, half_size - self.line_width, self.line_width))
        # Right rectangle
        pygame.draw.rect(self.image, self.color, (half_size + self.line_width, half_size - self.line_width // 2, half_size - self.line_width, self.line_width))

    def update(self):
        self.angle = (self.angle + self.rotation_speed) % 360
        self.draw_crosshair()
        original_center = self.rect.center
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.image.get_rect(center=original_center)
        self.rect.center = pygame.mouse.get_pos() # Follow mouse position

    def draw(self, screen):
        screen.blit(self.image, self.rect)


