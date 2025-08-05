import pygame
import random
import math

class StarParticle:
    def __init__(self, x, y, speed, size):
        self.x = x
        self.y = y
        self.speed = speed
        self.size = size
        self.alpha = random.randint(100, 255)
        self.fade_direction = random.choice([-1, 1])

    def update(self):
        # Move star horizontally (left to right)
        self.x += self.speed
        
        # Fade in and out
        self.alpha += self.fade_direction * 2
        if self.alpha <= 100:
            self.alpha = 100
            self.fade_direction = 1
        elif self.alpha >= 255:
            self.alpha = 255
            self.fade_direction = -1

    def draw(self, screen):
        # Draw a simple white pixel with alpha
        pixel_color = (255, 255, 255, self.alpha)
        pixel_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pixel_surface.fill(pixel_color)
        screen.blit(pixel_surface, (self.x, self.y))

class StarParticleSystem:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.stars = []
        self.spawn_timer = 0
        self.spawn_rate = 30  # frames between spawns (reduced quantity)

    def update(self):
        # Spawn new stars
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_rate:
            self.spawn_timer = 0
            self.spawn_star()

        # Update existing stars
        for star in self.stars[:]:  # Use slice to avoid modification during iteration
            star.update()
            
            # Remove stars that have moved off screen
            if star.x > self.screen_width + star.size:
                self.stars.remove(star)

    def spawn_star(self):
        # Spawn stars from the left side of the screen
        x = -10
        y = random.randint(0, self.screen_height)
        speed = random.uniform(0.5, 2.0)
        size = random.randint(2, 5)
        
        star = StarParticle(x, y, speed, size)
        self.stars.append(star)

    def draw(self, screen):
        for star in self.stars:
            star.draw(screen)