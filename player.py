import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color, screen_height, screen_width):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 0 # Initial speed for movement
        self.acceleration_base = 3 # Base acceleration for normal movement
        self.screen_height = screen_height
        self.screen_width = screen_width

        # Dash variables
        self.dash_active = False
        self.dash_velocity = 0
        self.dash_direction = 0 # 1 for up, -1 for down
        self.dash_decay = 0.89
        self.dash_initial_speed = 20
        self.dash_cooldown = 0
        self.dash_cooldown_time = 20 # frames of cooldown

        # Charge variables (for Player 1)
        self.charge_active = False
        self.charge_level = 0
        self.max_charge = 50
        self.charge_rate = 1
        self.charge_decay_rate = 10

    def move_up(self):
        self.speed = -self.acceleration_base

    def move_down(self):
        self.speed = self.acceleration_base

    def stop(self):
        self.speed = 0

    def update(self):
        # Normal movement
        self.rect.y += self.speed

        # Apply dash movement if active
        if self.dash_active:
            self.rect.y += (self.dash_velocity * self.dash_direction)
            self.dash_velocity *= self.dash_decay
            if abs(self.dash_velocity) < 1:
                self.dash_active = False

        # Update dash cooldown
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1

        # Update charge (for Player 1)
        if self.charge_active:
            self.charge_level = min(self.max_charge, self.charge_level + self.charge_rate)
            # Reduce normal movement speed while charging
            self.acceleration_base = 3 * 0.5 # Example: half normal speed
        else:
            self.charge_level = max(0, self.charge_level - self.charge_decay_rate)
            self.acceleration_base = 3 # Restore normal speed

        # Boundary checking
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > self.screen_height:
            self.rect.bottom = self.screen_height

    def start_dash(self, direction):
        if self.dash_cooldown <= 0 and not self.charge_active:
            self.dash_active = True
            self.dash_velocity = self.dash_initial_speed
            self.dash_direction = direction
            self.dash_cooldown = self.dash_cooldown_time
            # Visual feedback for dash (color change)
            self.image.fill((173, 216, 230)) # Lightblue

    def end_dash(self):
        if not self.dash_active and not self.charge_active:
            self.image.fill((255, 255, 255)) # White

    def start_charge(self):
        self.charge_active = True
        self.image.fill((255, 255, 0)) # Yellow

    def stop_charge(self):
        self.charge_active = False
        self.image.fill((128, 128, 128)) # Gray


class HumanPlayer(Player):
    def __init__(self, x, y, width, height, color, screen_height, screen_width):
        super().__init__(x, y, width, height, color, screen_height, screen_width)
        self.current_speed = 0
        self.acceleration = 0.9 # Acceleration for mouse control

    def update(self, target_y):
        # Move towards target_y (mouse y-coordinate)
        y_diff = target_y - self.rect.centery
        if abs(y_diff) > self.acceleration:
            if y_diff > 0:
                self.rect.y += self.acceleration
            else:
                self.rect.y -= self.acceleration
        else:
            self.rect.centery = target_y

        # Apply dash movement if active
        if self.dash_active:
            self.rect.y += (self.dash_velocity * self.dash_direction)
            self.dash_velocity *= self.dash_decay
            if abs(self.dash_velocity) < 1:
                self.dash_active = False

        # Update dash cooldown
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1

        # Update charge (for Player 1)
        if self.charge_active:
            self.charge_level = min(self.max_charge, self.charge_level + self.charge_rate)
            # Reduce normal movement speed while charging
            self.acceleration_base = 3 * 0.5 # Example: half normal speed
        else:
            self.charge_level = max(0, self.charge_level - self.charge_decay_rate)
            self.acceleration_base = 3 # Restore normal speed

        # Boundary checking
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > self.screen_height:
            self.rect.bottom = self.screen_height

        # Restore color after dash
        if not self.dash_active and not self.charge_active and self.image.get_at((0,0)) != (255, 255, 255, 255):
            self.image.fill((255, 255, 255)) # White


class AIPlayer(Player):
    def __init__(self, x, y, width, height, color, screen_height, screen_width):
        super().__init__(x, y, width, height, color, screen_height, screen_width)
        self.current_speed = 0
        self.acceleration = 0.9 # AI acceleration
        self.max_speed = 11
        self.min_speed = 1
        self.dash_initial_speed = 45 # AI dash is slightly different
        self.dash_cooldown_time = 19
        self.dash_trigger_distance = 100

    def update(self, ball_x, ball_y):
        # AI logic to follow the ball
        target_y = ball_y
        y_diff = target_y - self.rect.centery

        # AI Dash logic: only dash if ball is approaching and far enough
        if (self.dash_cooldown <= 0 and not self.dash_active and 
            abs(y_diff) > self.dash_trigger_distance and 
            ((self.rect.centerx < ball_x and ball_x > self.screen_width / 2) or 
             (self.rect.centerx > ball_x and ball_x < self.screen_width / 2))): # Ball is approaching
            
            self.start_dash(1 if y_diff > 0 else -1)
            self.image.fill((255, 0, 0)) # Red for AI dash

        # Normal AI movement if not dashing
        if not self.dash_active:
            if abs(y_diff) > 50:
                self.current_speed += self.acceleration * 2
            else:
                self.current_speed += self.acceleration

            self.current_speed = min(self.current_speed, self.max_speed)
            self.current_speed = max(self.current_speed, self.min_speed)

            if y_diff > 0:
                self.rect.y += self.current_speed
            else:
                self.rect.y -= self.current_speed

        # Apply dash movement if active (overrides normal movement)
        if self.dash_active:
            self.rect.y += (self.dash_velocity * self.dash_direction)
            self.dash_velocity *= self.dash_decay
            if abs(self.dash_velocity) < 1:
                self.dash_active = False

        # Update dash cooldown
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1

        # Boundary checking
        if self.rect.top < 0:
            self.rect.top = 0
            self.current_speed = self.min_speed
        if self.rect.bottom > self.screen_height:
            self.rect.bottom = self.screen_height
            self.current_speed = self.min_speed

        # Restore color after dash
        if not self.dash_active and self.image.get_at((0,0)) != (255, 255, 255, 255):
            self.image.fill((255, 255, 255)) # White