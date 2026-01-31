import pygame
import os

class SoundManager:
    """
    Handles sound effects for the libtcod roguelike.
    """
    def __init__(self):
        # Initialize mixer if not already done
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
        self.sounds = {}
        self.base_path = "sounds"
        self._load_all_sounds()

    def _load_all_sounds(self):
        """Loads specific wav files into the sound dictionary."""
        sound_files = {
            "player_hit": "player_hit.wav",
            "player_hurt": "player_hurt.wav",
            "soft_enemy_hit": "soft_enemy_hit.wav",
            "soft_enemy_hurt": "soft_enemy_hurt.wav",
            "hard_enemy_hit": "hard_enemy_hit.wav",
            "miss": "miss.wav",
            "move": "move.wav",
            "heal": "heal.wav",
        }
        
        for key, filename in sound_files.items():
            full_path = os.path.join(self.base_path, filename)
            if os.path.exists(full_path):
                self.sounds[key] = pygame.mixer.Sound(full_path)
            else:
                print(f"Note: {full_path} not found, sound '{key}' will be silent.")

    def play_sound(self, name: str):
        """Plays a sound by key name."""
        sound = self.sounds.get(name)
        if sound:
            sound.play()

# Create a single instance to be used across the game
# In actions.py, you can now use: from soundmanager import SoundManager
