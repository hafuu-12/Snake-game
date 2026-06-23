"""
achievements.py

Small achievement system. Nothing fancy - just a dict of achievements
with a condition that gets checked at the right moments, and they stay
unlocked forever once you get them (saved through StatsManager).
"""


class AchievementManager:
    def __init__(self):
        # using a dict so I can look achievements up by id easily,
        # order doesn't matter much for logic but I kept it in the
        # order they're listed in the assignment
        self.achievements = {
            "first_food": {
                "name": "First Bite",
                "desc": "Eat your first piece of food",
                "unlocked": False,
            },
            "score_50": {
                "name": "Half Century",
                "desc": "Reach a score of 50 in one run",
                "unlocked": False,
            },
            "score_100": {
                "name": "Century Club",
                "desc": "Reach a score of 100 in one run",
                "unlocked": False,
            },
            "survivor": {
                "name": "Survivor",
                "desc": "Survive for 3 minutes in a single run",
                "unlocked": False,
            },
        }

    def load_from_dict(self, saved_data):
        # merges saved unlocked states back in - called once on startup
        for key, val in saved_data.items():
            if key in self.achievements:
                self.achievements[key]["unlocked"] = val.get("unlocked", False)

    def to_dict(self):
        return {k: {"unlocked": v["unlocked"]} for k, v in self.achievements.items()}

    def check(self, score, food_eaten_this_run, survive_time_ms):
        """
        Call this during gameplay (or right at game over). Returns a list
        of achievement names that got newly unlocked this call, so the
        game can pop up a little "achievement unlocked" message.
        """
        newly_unlocked = []

        if food_eaten_this_run >= 1:
            newly_unlocked += self._unlock("first_food")

        if score >= 50:
            newly_unlocked += self._unlock("score_50")

        if score >= 100:
            newly_unlocked += self._unlock("score_100")

        if survive_time_ms >= 3 * 60 * 1000:
            newly_unlocked += self._unlock("survivor")

        return newly_unlocked

    def _unlock(self, key):
        if not self.achievements[key]["unlocked"]:
            self.achievements[key]["unlocked"] = True
            return [self.achievements[key]["name"]]
        return []

    def get_all(self):
        return self.achievements
