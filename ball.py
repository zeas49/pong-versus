import pygame
import math

class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y, size, color, screen_width, screen_height):
        super().__init__()
        self.size = size
        self.base_size = size
        self.image = pygame.Surface([size, size])
        self.image.fill(color)
        self.base_image = self.image.copy() # Store a base image
        self.rect = self.image.get_rect(center=(x, y))
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Ball physics
        self.dx = 0.5
        self.dy = 0.5
        self.dz = 0.5
        self.ax = 0.02
        self.ay = 0.01
        self.az = 0.01
        self.max_dx = 8
        self.max_dy = 2
        self.max_dz = 15
        self.initial_dx = self.dx
        self.initial_dy = self.dy

        # Wind trail system
        self.wind_trail = []
        self.max_trail_length = 8
        self.wind_trail_surfaces = []
        for i in range(self.max_trail_length):
            trail_surface = pygame.Surface([self.base_size, self.base_size], pygame.SRCALPHA)
            trail_surface.fill((255, 255, 255))
            self.wind_trail_surfaces.append(trail_surface)

    def update(self):
        # Wall curve avoidance logic
        wall_proximity_threshold = 280
        curve_strength = 0.2

        # Check proximity to top wall
        if self.rect.centery < wall_proximity_threshold and self.dy < 0:
            self.dy += curve_strength
            self.ay += curve_strength * 0.1

        # Check proximity to bottom wall
        elif self.rect.centery > (self.screen_height - wall_proximity_threshold) and self.dy > 0:
            self.dy -= curve_strength
            self.ay -= curve_strength * 0.1

        # Horizontal acceleration
        if self.dx > 0:
            if self.dx < self.max_dx:
                self.dx += self.ax
        else:
            if self.dx > -self.max_dx:
                self.dx -= self.ax

        # Vertical acceleration
        if self.dx > 0:
            if self.dy < self.max_dy:
                self.dy += self.ay

        if self.dx < 0:
            if self.dy < -self.max_dy:
                self.dy -= self.ay

        # Z acceleration (for 3D effect)
        if self.dz < self.max_dz:
            self.dz += self.az

        # Ball movement
        self.rect.x += self.dx
        self.rect.y += self.dy

        # 3D size effect simulation
        distance_from_center_x = abs(self.rect.centerx - self.screen_width / 2)
        max_distance_x = self.screen_width / 2

        normalized_distance = distance_from_center_x / max_distance_x

        trajectory_angle = math.atan2(self.dy, self.dx) if self.dx != 0 else 0
        angle_factor = abs(math.sin(trajectory_angle))

        base_size_factor = normalized_distance * 295
        angle_size_factor = angle_factor * 300 # Efeito adicional baseado no ângulo
        velocity_factor = (abs(self.dx) + abs(self.dy)) * -13.5 # Efeito baseado na velocidade

        self.size = base_size_factor + angle_size_factor + velocity_factor + self.base_size
        self.size = max(29, min(self.size, 152))

        # Update ball visual size
        self.image = pygame.transform.scale(self.base_image, (int(self.size), int(self.size)))
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center

        # Update wind trail
        self.update_wind_trail()

        # Wall collision
        if self.rect.top <= self.screen_height / 2 - 280:
            self.rect.top = self.screen_height / 2 - 280
            self.dy *= -1
            self.ay *= -1
            self.dx *= 0.95
            self.dy *= 0.95

        if self.rect.bottom >= self.screen_height / 2 + 280:
            self.rect.bottom = self.screen_height / 2 + 280
            self.dy *= -1
            self.ay *= -1
            self.dx *= 0.95
            self.dy *= 0.95

    def update_wind_trail(self):
        # Add current position to trail
        self.wind_trail.insert(0, (self.rect.centerx, self.rect.centery, self.size))

        # Limit trail length
        if len(self.wind_trail) > self.max_trail_length:
            self.wind_trail.pop()

    def draw_wind_trail(self, screen):
        for i, (x, y, size) in enumerate(self.wind_trail):
            if i < len(self.wind_trail_surfaces):
                opacity = 1.0 - (i / self.max_trail_length)
                alpha = int(255 * opacity)
                
                # Scale and set alpha for the pre-rendered surface
                scaled_surface = pygame.transform.scale(self.wind_trail_surfaces[i], (int(size), int(size)))
                scaled_surface.set_alpha(alpha)
                
                screen.blit(scaled_surface, (x - size // 2, y - size // 2))

    def reset(self, x, y, direction=1):
        self.rect.center = (x, y)
        self.dx = self.initial_dx * direction
        self.dy = self.initial_dy
        self.wind_trail.clear()

    def reverse_x(self):
        self.dx *= -1
        self.dx *= 0.95
        self.dy *= 0.95
