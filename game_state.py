import json
import os
from pathlib import Path

class GameState:
    def __init__(self):
        self.save_file = "sokoban_save.json"
        self.current_level = 0
        self.scores = {}  # Format: {level_number: moves_count}
        self.load_game()

    def save_game(self):
        """Save the current game state to a file."""
        save_data = {
            'current_level': self.current_level,
            'scores': self.scores
        }
        try:
            with open(self.save_file, 'w') as f:
                json.dump(save_data, f)
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False

    def load_game(self):
        """Load the game state from file."""
        if not os.path.exists(self.save_file):
            return False
        
        try:
            with open(self.save_file, 'r') as f:
                save_data = json.load(f)
                self.current_level = save_data.get('current_level', 0)
                self.scores = save_data.get('scores', {})
            return True
        except Exception as e:
            print(f"Error loading game: {e}")
            return False

    def update_score(self, level, moves):
        """Update the score for a level if it's better than the previous best."""
        level_str = str(level)
        if level_str not in self.scores or moves < self.scores[level_str]:
            self.scores[level_str] = moves
            self.save_game()

    def get_score(self, level):
        """Get the best score for a level."""
        return self.scores.get(str(level), None)

    def advance_level(self):
        """Advance to the next level."""
        self.current_level += 1
        self.save_game()

    def set_level(self, level):
        """Set the current level."""
        self.current_level = level
        self.save_game() 