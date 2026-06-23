"""
stats_manager.py

Handles the "save your progress" stuff - games played, total score,
total food eaten, and the achievements dict. All saved together in one
progress.json file in /data.

NOTE: the high score itself is ALSO saved separately in a plain
highscore.txt file (see settings.HIGHSCORE_FILE / the load/save
functions in game.py). That's a leftover from how I originally built
this before adding the stats system - the simple txt version still
works fine so I just left both in instead of refactoring it all into one.
"""

import json
import os
from settings import PROGRESS_FILE


class StatsManager:
    def __init__(self):
        self.games_played = 0
        self.total_score = 0
        self.total_food_eaten = 0
        self.high_score = 0
        self.achievements_data = {}
        self.load()

    def load(self):
        if not os.path.exists(PROGRESS_FILE):
            return  # first time running the game, just keep the defaults
        try:
            with open(PROGRESS_FILE, "r") as f:
                data = json.load(f)
            self.games_played = data.get("games_played", 0)
            self.total_score = data.get("total_score", 0)
            self.total_food_eaten = data.get("total_food_eaten", 0)
            self.high_score = data.get("high_score", 0)
            self.achievements_data = data.get("achievements", {})
        except (json.JSONDecodeError, OSError):
            # if the file got corrupted somehow, don't crash the whole game
            # over it, just start fresh
            print("couldn't read progress file, starting with fresh stats")

    def save(self):
        data = {
            "games_played": self.games_played,
            "total_score": self.total_score,
            "total_food_eaten": self.total_food_eaten,
            "high_score": self.high_score,
            "achievements": self.achievements_data,
        }
        try:
            with open(PROGRESS_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except OSError:
            print("warning: couldn't save progress file")

    def record_game(self, score, food_eaten):
        self.games_played += 1
        self.total_score += score
        self.total_food_eaten += food_eaten
        if score > self.high_score:
            self.high_score = score
        self.save()

    def average_score(self):
        if self.games_played == 0:
            return 0
        return round(self.total_score / self.games_played, 1)
