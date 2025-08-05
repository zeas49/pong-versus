import pygame
import os

class SoundManager:
    def __init__(self):
        try:
            pygame.mixer.init()
            self.sound_enabled = True
            self.sounds = {}
        except pygame.error:
            print("Warning: Could not initialize Pygame mixer. Sound will be disabled.")
            self.sound_enabled = False
            self.sounds = {}
        self.load_sounds()

    def load_sounds(self):
        sound_files = {
            'player_colide': 'player_colide.wav',
            'silence': 'silence.wav',
            'hit': 'hit.wav',
            'charge': 'charge.wav',
            'point': 'fall.wav',
            'enter': 'enter.wav',
            'speed': 'speed.wav'
        }

        for sound_name, filename in sound_files.items():
            try:
                if os.path.exists(filename):
                    self.sounds[sound_name] = pygame.mixer.Sound(filename)
                else:
                    # Create a silent sound if file doesn't exist
                    self.sounds[sound_name] = None
            except pygame.error:
                self.sounds[sound_name] = None

    def play_sound(self, sound_name):
        if self.sound_enabled and sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].play()

