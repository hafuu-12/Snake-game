"""
main.py

Entry point. Run this file to play the game:
    python main.py

Everything else is split across the other files in this folder.
"""

from game import Game

if __name__ == "__main__":
    game = Game()
    game.run()
