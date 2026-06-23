"""
game.py

This is the big one. The Game class runs the whole show - main menu,
settings, the actual gameplay, pause screen, game over screen, stats
screen, all of it. Probably could've split this into more files but
honestly keeping the state machine in one place made it way easier to
keep track of what screen does what while I was building this.

States (self.state) used:
    MENU, DIFFICULTY, SETTINGS, INSTRUCTIONS, STATS, COUNTDOWN,
    PLAYING, PAUSED, GAMEOVER
"""

import os
import random
import pygame

import settings
from snake import Snake
from food import Food, BonusFood
from obstacle import Obstacle
from powerup import PowerUp
from particle import ParticleSystem, FloatingShape
from button import Menu
from achievements import AchievementManager
from stats_manager import StatsManager


def load_highscore():
    # plain text file, just one number in it
    if not os.path.exists(settings.HIGHSCORE_FILE):
        return 0
    try:
        with open(settings.HIGHSCORE_FILE, "r") as f:
            content = f.read().strip()
            return int(content) if content else 0
    except (ValueError, OSError):
        return 0


def save_highscore(value):
    try:
        with open(settings.HIGHSCORE_FILE, "w") as f:
            f.write(str(value))
    except OSError:
        print("warning: could not save high score file")


class Game:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
        except pygame.error:
            # if there's no audio device available the game should still
            # run, just silently
            print("no audio device found, sound will be disabled")

        # ----- default settings, can be changed from the Settings menu -----
        self.board_size_name = "Medium"
        self.cols, self.rows = settings.BOARD_SIZES[self.board_size_name]
        self.theme_name = "Classic Green"
        self.difficulty = "Medium"
        self.day_mode = True
        self.muted = False

        self.screen = None
        self._rebuild_screen()
        pygame.display.set_caption("Snake Game - CS Project")

        self.clock = pygame.time.Clock()

        self.font_small = pygame.font.SysFont(None, 22)
        self.font_med = pygame.font.SysFont(None, 30)
        self.font_big = pygame.font.SysFont(None, 56)
        self.font_title = pygame.font.SysFont(None, 80)

        self._load_sounds()

        self.high_score = load_highscore()
        self.stats = StatsManager()
        # keep the txt high score and the json one in sync, in case one
        # of the files is missing/out of date compared to the other
        if self.stats.high_score > self.high_score:
            self.high_score = self.stats.high_score
        elif self.high_score > self.stats.high_score:
            self.stats.high_score = self.high_score

        self.achievements = AchievementManager()
        self.achievements.load_from_dict(self.stats.achievements_data)

        self.menu_shapes = [FloatingShape(*self.screen.get_size()) for _ in range(14)]

        self.state = "MENU"
        self.running = True

        self.toast_message = ""
        self.toast_timer = 0

        self._build_menus()
        self._reset_game_state()

    # ------------------------------------------------------------------
    # setup helpers
    # ------------------------------------------------------------------

    def _rebuild_screen(self):
        width = self.cols * settings.TILE_SIZE
        height = self.rows * settings.TILE_SIZE + settings.HUD_HEIGHT
        # menus need a bit more room than tiny boards, so enforce a minimum
        width = max(width, 560)
        height = max(height, 480)
        self.screen = pygame.display.set_mode((width, height))

    def _load_sounds(self):
        self.snd_eat = self._safe_load_sound(os.path.join(settings.SOUND_DIR, "eat.wav"))
        self.snd_bonus = self._safe_load_sound(os.path.join(settings.SOUND_DIR, "bonus.wav"))
        self.snd_gameover = self._safe_load_sound(os.path.join(settings.SOUND_DIR, "gameover.wav"))

        music_path = os.path.join(settings.MUSIC_DIR, "background.wav")
        self.music_loaded = False
        if os.path.exists(music_path) and pygame.mixer.get_init():
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.3)
                self.music_loaded = True
            except pygame.error:
                self.music_loaded = False

    def _safe_load_sound(self, path):
        if not pygame.mixer.get_init():
            return None
        if not os.path.exists(path):
            return None
        try:
            return pygame.mixer.Sound(path)
        except pygame.error:
            return None

    def _play_sound(self, sound):
        if sound and not self.muted:
            sound.play()

    def _build_menus(self):
        """(Re)builds all the button menus. Called on startup and again
        whenever the screen size changes (board size setting)."""
        w, h = self.screen.get_size()
        cx = w // 2
        btn_w, btn_h, gap = 240, 50, 16

        self.main_menu = Menu()
        start_y = h // 2 - 60
        self.main_menu.add_button((cx - btn_w // 2, start_y, btn_w, btn_h), "Start Game", "start", self.font_med)
        self.main_menu.add_button((cx - btn_w // 2, start_y + (btn_h + gap), btn_w, btn_h), "Instructions", "instructions", self.font_med)
        self.main_menu.add_button((cx - btn_w // 2, start_y + 2 * (btn_h + gap), btn_w, btn_h), "Settings", "settings", self.font_med)
        self.main_menu.add_button((cx - btn_w // 2, start_y + 3 * (btn_h + gap), btn_w, btn_h), "Statistics", "stats", self.font_med)
        self.main_menu.add_button((cx - btn_w // 2, start_y + 4 * (btn_h + gap), btn_w, btn_h), "Exit", "exit", self.font_med, base_color=(120, 50, 50), hover_color=(160, 60, 60))

        self.difficulty_menu = Menu()
        d_y = h // 2 - 70
        for i, level in enumerate(["Easy", "Medium", "Hard"]):
            self.difficulty_menu.add_button((cx - btn_w // 2, d_y + i * (btn_h + gap), btn_w, btn_h), level, f"diff_{level}", self.font_med)
        self.difficulty_menu.add_button((cx - btn_w // 2, d_y + 3 * (btn_h + gap) + 10, btn_w, btn_h), "Back", "back_to_menu", self.font_small)

        self.settings_menu = Menu()
        col1_x = cx - btn_w - 20
        col2_x = cx + 20
        s_y = 130
        for i, theme in enumerate(settings.THEMES.keys()):
            self.settings_menu.add_button((col1_x, s_y + i * (btn_h + 10), btn_w, btn_h), theme, f"theme_{theme}", self.font_small)

        for i, size_name in enumerate(settings.BOARD_SIZES.keys()):
            self.settings_menu.add_button((col2_x, s_y + i * (btn_h + 10), btn_w, btn_h), f"Board: {size_name}", f"board_{size_name}", self.font_small)

        toggle_y = s_y + len(settings.BOARD_SIZES) * (btn_h + 10) + 20
        self.settings_menu.add_button((col2_x, toggle_y, btn_w, btn_h), "Toggle Day/Night", "toggle_daynight", self.font_small)
        self.settings_menu.add_button((col2_x, toggle_y + btn_h + 10, btn_w, btn_h), "Toggle Mute", "toggle_mute", self.font_small)

        self.settings_menu.add_button((cx - btn_w // 2, h - 70, btn_w, btn_h), "Back", "back_to_menu", self.font_small)

        self.simple_back_menu = Menu()
        self.simple_back_menu.add_button((cx - btn_w // 2, h - 70, btn_w, btn_h), "Back", "back_to_menu", self.font_small)

        self.pause_menu = Menu()
        p_y = h // 2 - 50
        self.pause_menu.add_button((cx - btn_w // 2, p_y, btn_w, btn_h), "Resume", "resume", self.font_med)
        self.pause_menu.add_button((cx - btn_w // 2, p_y + btn_h + gap, btn_w, btn_h), "Main Menu", "back_to_menu", self.font_med)

        self.gameover_menu = Menu()
        g_y = h // 2 + 40
        self.gameover_menu.add_button((cx - btn_w // 2, g_y, btn_w, btn_h), "Play Again", "restart", self.font_med)
        self.gameover_menu.add_button((cx - btn_w // 2, g_y + btn_h + gap, btn_w, btn_h), "Main Menu", "back_to_menu", self.font_med)

    def _reset_game_state(self):
        """Resets everything needed for a fresh run of the snake game itself
        (not the overall app state, just the gameplay bits)."""
        start_x = self.cols // 2
        start_y = self.rows // 2
        self.snake = Snake(start_x, start_y, settings.THEMES[self.theme_name])

        self.food = Food(self.cols, self.rows, settings.TILE_SIZE)
        self.food.respawn(self.snake.body)

        self.bonus_food = BonusFood(settings.TILE_SIZE, settings.BONUS_FOOD_LIFETIME, settings.BONUS_FOOD_POINTS)
        self.bonus_spawn_cooldown = random.randint(7000, 14000)
        self.bonus_last_check = pygame.time.get_ticks()

        self.obstacles = Obstacle(settings.OBSTACLE_SCORE_MILESTONE, settings.OBSTACLES_PER_MILESTONE)
        self.powerup = PowerUp(settings.TILE_SIZE)

        self.particles = ParticleSystem()

        self.score = 0
        self.food_eaten_this_run = 0
        self.move_timer = 0
        self.base_move_interval = settings.DIFFICULTY_SPEEDS[self.difficulty]

        # active power-up effects: name -> time it should end (ms since pygame start)
        self.active_effects = {}
        self.score_multiplier = 1

        self.run_start_time = pygame.time.get_ticks()
        self.countdown_start = 0
        self.countdown_value = 3

        self.newly_unlocked_achievements = []

    # ------------------------------------------------------------------
    # main loop
    # ------------------------------------------------------------------

    def run(self):
        while self.running:
            dt = self.clock.tick(settings.FPS)
            mouse_pos = pygame.mouse.get_pos()

            self._handle_events(mouse_pos)
            self._update(dt)
            self._draw(mouse_pos)

            pygame.display.flip()

        pygame.quit()

    # ------------------------------------------------------------------
    # events
    # ------------------------------------------------------------------

    def _handle_events(self, mouse_pos):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(mouse_pos)

    def _handle_keydown(self, key):
        if key == pygame.K_ESCAPE:
            if self.state in ("PLAYING", "PAUSED"):
                self.state = "MENU"
                self._stop_music()
            elif self.state != "MENU":
                self.state = "MENU"

        if self.state == "PLAYING":
            if key in (pygame.K_UP, pygame.K_w):
                self.snake.change_direction((0, -1))
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.snake.change_direction((0, 1))
            elif key in (pygame.K_LEFT, pygame.K_a):
                self.snake.change_direction((-1, 0))
            elif key in (pygame.K_RIGHT, pygame.K_d):
                self.snake.change_direction((1, 0))
            elif key == pygame.K_p:
                self.state = "PAUSED"
            elif key == pygame.K_m:
                self._toggle_mute()

        elif self.state == "PAUSED":
            if key == pygame.K_p:
                self.state = "PLAYING"

        elif self.state == "GAMEOVER":
            if key == pygame.K_RETURN:
                self._start_countdown()
            elif key == pygame.K_m:
                self._toggle_mute()

    def _handle_click(self, mouse_pos):
        if self.state == "MENU":
            action = self.main_menu.get_clicked_action(mouse_pos)
            self._handle_menu_action(action)

        elif self.state == "DIFFICULTY":
            action = self.difficulty_menu.get_clicked_action(mouse_pos)
            self._handle_menu_action(action)

        elif self.state == "SETTINGS":
            action = self.settings_menu.get_clicked_action(mouse_pos)
            self._handle_menu_action(action)

        elif self.state in ("INSTRUCTIONS", "STATS"):
            action = self.simple_back_menu.get_clicked_action(mouse_pos)
            self._handle_menu_action(action)

        elif self.state == "PAUSED":
            action = self.pause_menu.get_clicked_action(mouse_pos)
            self._handle_menu_action(action)

        elif self.state == "GAMEOVER":
            action = self.gameover_menu.get_clicked_action(mouse_pos)
            self._handle_menu_action(action)

    def _handle_menu_action(self, action):
        if action is None:
            return

        if action == "start":
            self.state = "DIFFICULTY"
        elif action == "instructions":
            self.state = "INSTRUCTIONS"
        elif action == "settings":
            self.state = "SETTINGS"
        elif action == "stats":
            self.state = "STATS"
        elif action == "exit":
            self.running = False
        elif action == "back_to_menu":
            self.state = "MENU"
            self._stop_music()
        elif action == "resume":
            self.state = "PLAYING"
        elif action == "restart":
            self._start_countdown()

        elif action.startswith("diff_"):
            self.difficulty = action.split("_", 1)[1]
            self._start_countdown()

        elif action.startswith("theme_"):
            self.theme_name = action.split("_", 1)[1]
            self.snake.set_theme(settings.THEMES[self.theme_name]) if hasattr(self, "snake") else None

        elif action.startswith("board_"):
            new_size = action.split("_", 1)[1]
            if new_size != self.board_size_name:
                self.board_size_name = new_size
                self.cols, self.rows = settings.BOARD_SIZES[new_size]
                self._rebuild_screen()
                self._build_menus()

        elif action == "toggle_daynight":
            self.day_mode = not self.day_mode
        elif action == "toggle_mute":
            self._toggle_mute()

    def _toggle_mute(self):
        self.muted = not self.muted
        if self.muted:
            pygame.mixer.music.set_volume(0)
        else:
            pygame.mixer.music.set_volume(0.3)

    def _start_countdown(self):
        self._reset_game_state()
        self.state = "COUNTDOWN"
        self.countdown_start = pygame.time.get_ticks()
        self.countdown_value = 3
        self._play_music()

    def _play_music(self):
        if self.music_loaded and not self.muted:
            try:
                pygame.mixer.music.play(loops=-1)
            except pygame.error:
                pass

    def _stop_music(self):
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()

    # ------------------------------------------------------------------
    # update
    # ------------------------------------------------------------------

    def _update(self, dt):
        if self.state == "MENU":
            w, h = self.screen.get_size()
            for shape in self.menu_shapes:
                shape.update(w, h)

        elif self.state == "COUNTDOWN":
            elapsed = pygame.time.get_ticks() - self.countdown_start
            self.countdown_value = 3 - elapsed // 1000
            if self.countdown_value <= 0:
                self.state = "PLAYING"

        elif self.state == "PLAYING":
            self._update_playing(dt)

        # expire the achievement toast after a few seconds
        if self.toast_message and pygame.time.get_ticks() - self.toast_timer > 2500:
            self.toast_message = ""

    def _current_move_interval(self):
        floor = settings.MIN_MOVE_INTERVAL[self.difficulty]
        speedup_steps = self.score // settings.SPEEDUP_EVERY_N_POINTS
        interval = self.base_move_interval - speedup_steps * settings.SPEEDUP_AMOUNT_MS
        interval = max(floor, interval)

        if "slow" in self.active_effects:
            interval = int(interval * 1.7)

        return interval

    def _update_playing(self, dt):
        now = pygame.time.get_ticks()

        # expire timed power-up effects
        expired = [name for name, end in self.active_effects.items() if now > end]
        for name in expired:
            del self.active_effects[name]
            if name == "double":
                self.score_multiplier = 1

        self.bonus_food.update()
        self.powerup.update(self.cols, self.rows, self._all_blocked_cells())

        # bonus food spawn timer (separate from the BonusFood's own lifetime timer)
        if not self.bonus_food.active and now - self.bonus_last_check > self.bonus_spawn_cooldown:
            self.bonus_food.spawn(self.cols, self.rows, self._all_blocked_cells())
            self.bonus_last_check = now
            self.bonus_spawn_cooldown = random.randint(8000, 15000)

        self.particles.update()

        # movement is timer based instead of tied to fps, otherwise the
        # snake's speed would depend on how fast the computer running it is
        self.move_timer += dt
        move_interval = self._current_move_interval()
        if self.move_timer >= move_interval:
            self.move_timer = 0
            self._step_snake()

    def _all_blocked_cells(self):
        blocked = set(self.snake.body)
        blocked.add(self.food.pos)
        blocked.update(self.obstacles.blocks)
        return blocked

    def _step_snake(self):
        self.snake.move()
        head = self.snake.get_head()

        # wall / self / obstacle collisions
        hit_wall = self.snake.check_wall_collision(self.cols, self.rows)
        hit_self = self.snake.check_self_collision()
        hit_obstacle = self.obstacles.collides(head)

        if hit_wall or hit_self or hit_obstacle:
            if self.snake.shield_active:
                # shield absorbs the hit - consume it and nudge the snake
                # back into bounds/away from the obstacle so it's not
                # immediately stuck colliding again next frame
                self.snake.shield_active = False
                self.snake.body.pop(0)  # undo the move that caused the crash
                self.toast_message = "Shield absorbed the hit!"
                self.toast_timer = pygame.time.get_ticks()
                return
            else:
                self._game_over()
                return

        # food
        if head == self.food.pos:
            self._eat_food()

        # bonus food
        if self.bonus_food.active and head == self.bonus_food.pos:
            self._eat_bonus_food()

        # power-up pickup
        if self.powerup.active and head == self.powerup.pos:
            self._collect_powerup()

    def _eat_food(self):
        points = 1 * self.score_multiplier
        self.score += points
        self.food_eaten_this_run += 1
        self.snake.grow(1)
        self._play_sound(self.snd_eat)

        fx, fy = self.food.pos
        px = fx * settings.TILE_SIZE + settings.TILE_SIZE // 2
        py = fy * settings.TILE_SIZE + settings.TILE_SIZE // 2 + settings.HUD_HEIGHT
        self.particles.burst(px, py, (210, 45, 45), count=14)

        self.food.respawn(self._all_blocked_cells())
        self.obstacles.maybe_add_blocks(self.score, self.cols, self.rows, self._all_blocked_cells())
        self._check_achievements()

    def _eat_bonus_food(self):
        points = self.bonus_food.points * self.score_multiplier
        self.score += points
        self.food_eaten_this_run += 1
        self.snake.grow(2)  # bonus food makes you grow a bit more, feels rewarding
        self._play_sound(self.snd_bonus)

        bx, by = self.bonus_food.pos
        px = bx * settings.TILE_SIZE + settings.TILE_SIZE // 2
        py = by * settings.TILE_SIZE + settings.TILE_SIZE // 2 + settings.HUD_HEIGHT
        self.particles.burst(px, py, (255, 200, 0), count=24)

        self.bonus_food.active = False
        self._check_achievements()

    def _collect_powerup(self):
        kind = self.powerup.kind
        now = pygame.time.get_ticks()

        if kind == "shield":
            self.snake.shield_active = True
        else:
            self.active_effects[kind] = now + settings.POWERUP_DURATION[kind]
            if kind == "double":
                self.score_multiplier = 2

        self.toast_message = f"{settings.POWERUP_NAMES[kind]} activated!"
        self.toast_timer = now
        self.powerup.active = False

    def _check_achievements(self):
        survive_time = pygame.time.get_ticks() - self.run_start_time
        unlocked = self.achievements.check(self.score, self.food_eaten_this_run, survive_time)
        if unlocked:
            self.newly_unlocked_achievements.extend(unlocked)
            self.toast_message = "Achievement: " + ", ".join(unlocked)
            self.toast_timer = pygame.time.get_ticks()

    def _game_over(self):
        self._play_sound(self.snd_gameover)
        self._stop_music()

        survive_time = pygame.time.get_ticks() - self.run_start_time
        self.achievements.check(self.score, self.food_eaten_this_run, survive_time)

        if self.score > self.high_score:
            self.high_score = self.score
            save_highscore(self.high_score)

        self.stats.record_game(self.score, self.food_eaten_this_run)
        self.stats.high_score = self.high_score
        self.stats.achievements_data = self.achievements.to_dict()
        self.stats.save()

        self.state = "GAMEOVER"

    # ------------------------------------------------------------------
    # drawing
    # ------------------------------------------------------------------

    def _bg_color(self):
        return settings.DAY_BG if self.day_mode else settings.NIGHT_BG

    def _grid_color(self):
        return settings.DAY_GRID if self.day_mode else settings.NIGHT_GRID

    def _text_color(self):
        return settings.BLACK if self.day_mode else settings.WHITE

    def _draw(self, mouse_pos):
        self.screen.fill(self._bg_color())

        if self.state == "MENU":
            self._draw_menu(mouse_pos)
        elif self.state == "DIFFICULTY":
            self._draw_difficulty(mouse_pos)
        elif self.state == "SETTINGS":
            self._draw_settings(mouse_pos)
        elif self.state == "INSTRUCTIONS":
            self._draw_instructions(mouse_pos)
        elif self.state == "STATS":
            self._draw_stats(mouse_pos)
        elif self.state == "COUNTDOWN":
            self._draw_playfield()
            self._draw_countdown()
        elif self.state == "PLAYING":
            self._draw_playfield()
        elif self.state == "PAUSED":
            self._draw_playfield()
            self._draw_pause_overlay(mouse_pos)
        elif self.state == "GAMEOVER":
            self._draw_gameover(mouse_pos)

    def _draw_title(self, text, y):
        surf = self.font_title.render(text, True, self._text_color())
        rect = surf.get_rect(center=(self.screen.get_width() // 2, y))
        self.screen.blit(surf, rect)

    def _draw_menu(self, mouse_pos):
        for shape in self.menu_shapes:
            shape.draw(self.screen, (70, 140, 90) if self.day_mode else (90, 130, 170))

        self._draw_title("SNAKE", 90)
        sub = self.font_small.render("Designed by Me! Me!", True, self._text_color())
        self.screen.blit(sub, sub.get_rect(center=(self.screen.get_width() // 2, 140)))

        self.main_menu.draw(self.screen, mouse_pos)

        hs_text = self.font_small.render(f"High Score: {self.high_score}", True, self._text_color())
        self.screen.blit(hs_text, (12, self.screen.get_height() - 28))

    def _draw_difficulty(self, mouse_pos):
        self._draw_title("Select Difficulty", 80)
        self.difficulty_menu.draw(self.screen, mouse_pos)

    def _draw_settings(self, mouse_pos):
        self._draw_title("Settings", 70)
        label1 = self.font_small.render("Snake Theme", True, self._text_color())
        self.screen.blit(label1, (self.screen.get_width() // 2 - 240 - 20, 105))
        label2 = self.font_small.render("Board / Display", True, self._text_color())
        self.screen.blit(label2, (self.screen.get_width() // 2 + 20, 105))

        self.settings_menu.draw(self.screen, mouse_pos)

        current = self.font_small.render(
            f"Current: {self.theme_name} | {self.board_size_name} board | "
            f"{'Night' if not self.day_mode else 'Day'} mode | "
            f"{'Muted' if self.muted else 'Sound on'}",
            True, self._text_color(),
        )
        self.screen.blit(current, current.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() - 100)))

    def _draw_instructions(self, mouse_pos):
        self._draw_title("How To Play", 60)
        lines = [
            "Arrow Keys / WASD - move the snake",
            "P - pause / resume",
            "M - mute / unmute sound",
            "ESC - back to main menu",
            "",
            "Eat the red food to grow and score points.",
            "Gold blinking food = bonus food, worth more but it disappears fast.",
            "Glowing circles are power-ups:",
            "   S = Slow Motion, D = Double Points, P = Shield",
            "Grey blocks are obstacles - they start appearing as your score goes up.",
            "Watch out, hitting a wall, yourself, or an obstacle ends the game",
            "(unless you've got a shield active).",
        ]
        y = 120
        for line in lines:
            surf = self.font_small.render(line, True, self._text_color())
            self.screen.blit(surf, (40, y))
            y += 26

        self.simple_back_menu.draw(self.screen, mouse_pos)

    def _draw_stats(self, mouse_pos):
        self._draw_title("Statistics", 60)
        lines = [
            f"Highest Score: {self.high_score}",
            f"Total Games Played: {self.stats.games_played}",
            f"Average Score: {self.stats.average_score()}",
            f"Total Food Eaten: {self.stats.total_food_eaten}",
            "",
            "Achievements:",
        ]
        y = 130
        for line in lines:
            surf = self.font_small.render(line, True, self._text_color())
            self.screen.blit(surf, (60, y))
            y += 26

        for key, ach in self.achievements.get_all().items():
            status = "[X]" if ach["unlocked"] else "[ ]"
            line = f"  {status} {ach['name']} - {ach['desc']}"
            color = (40, 140, 40) if ach["unlocked"] else self._text_color()
            surf = self.font_small.render(line, True, color)
            self.screen.blit(surf, (60, y))
            y += 24

        self.simple_back_menu.draw(self.screen, mouse_pos)

    def _draw_playfield(self):
        # the grid lines - mostly decorative but it helps you judge
        # distance to the food/obstacles
        for x in range(self.cols + 1):
            xpix = x * settings.TILE_SIZE
            pygame.draw.line(self.screen, self._grid_color(), (xpix, settings.HUD_HEIGHT), (xpix, self.screen.get_height()))
        for y in range(self.rows + 1):
            ypix = y * settings.TILE_SIZE + settings.HUD_HEIGHT
            pygame.draw.line(self.screen, self._grid_color(), (0, ypix), (self.cols * settings.TILE_SIZE, ypix))

        self.obstacles.draw(self.screen, settings.TILE_SIZE, settings.HUD_HEIGHT)
        self.food.draw(self.screen, settings.HUD_HEIGHT)
        self.bonus_food.draw(self.screen, settings.HUD_HEIGHT)
        self.powerup.draw(self.screen, settings.HUD_HEIGHT)
        self.snake.draw(self.screen, settings.TILE_SIZE, settings.HUD_HEIGHT)
        self.particles.draw(self.screen)

        self._draw_hud()

        if self.toast_message:
            self._draw_toast()

    def _draw_hud(self):
        pygame.draw.rect(self.screen, (35, 35, 40) if not self.day_mode else (210, 215, 200),
                          (0, 0, self.screen.get_width(), settings.HUD_HEIGHT))

        score_surf = self.font_med.render(f"Score: {self.score}", True, self._text_color())
        self.screen.blit(score_surf, (14, 16))

        hs_surf = self.font_small.render(f"Best: {self.high_score}", True, self._text_color())
        self.screen.blit(hs_surf, (14, 42))

        diff_surf = self.font_small.render(f"{self.difficulty}", True, self._text_color())
        self.screen.blit(diff_surf, (self.screen.get_width() - 90, 10))

        # show active power-up effects so the player knows their buff is running out
        effects_text = []
        now = pygame.time.get_ticks()
        for name, end_time in self.active_effects.items():
            seconds_left = max(0, (end_time - now) // 1000 + 1)
            effects_text.append(f"{settings.POWERUP_NAMES[name]} ({seconds_left}s)")
        if self.snake.shield_active:
            effects_text.append("Shield up")

        if effects_text:
            eff_surf = self.font_small.render(" | ".join(effects_text), True, self._text_color())
            self.screen.blit(eff_surf, eff_surf.get_rect(center=(self.screen.get_width() // 2, 30)))

    def _draw_toast(self):
        surf = self.font_small.render(self.toast_message, True, (255, 255, 255))
        bg_rect = surf.get_rect(center=(self.screen.get_width() // 2, settings.HUD_HEIGHT + 24))
        bg_rect.inflate_ip(20, 10)
        pygame.draw.rect(self.screen, (30, 30, 30), bg_rect, border_radius=6)
        self.screen.blit(surf, surf.get_rect(center=bg_rect.center))

    def _draw_countdown(self):
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))

        text = str(self.countdown_value) if self.countdown_value > 0 else "GO!"
        surf = self.font_title.render(text, True, (255, 255, 255))
        self.screen.blit(surf, surf.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2)))

    def _draw_pause_overlay(self, mouse_pos):
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        title = self.font_big.render("PAUSED", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 110)))

        self.pause_menu.draw(self.screen, mouse_pos)

    def _draw_gameover(self, mouse_pos):
        self._draw_playfield()

        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        title = self.font_big.render("GAME OVER", True, (220, 60, 60))
        self.screen.blit(title, title.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 100)))

        score_surf = self.font_med.render(f"Final Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_surf, score_surf.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 50)))

        if self.score >= self.high_score and self.score > 0:
            new_hs = self.font_small.render("New High Score!", True, (250, 210, 60))
            self.screen.blit(new_hs, new_hs.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 20)))

        if self.newly_unlocked_achievements:
            ach_text = "Unlocked: " + ", ".join(self.newly_unlocked_achievements)
            ach_surf = self.font_small.render(ach_text, True, (180, 220, 255))
            self.screen.blit(ach_surf, ach_surf.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 8)))

        self.gameover_menu.draw(self.screen, mouse_pos)
