# Snake Game (Python / Pygame)

A Snake game I built for my programming class. Started out as the basic
"move around and eat food" version from the course slides, then I kept
adding stuff to it over the week because once I had the menu working it
was hard to stop adding features.

## Project Overview

This is a fairly complete arcade-style Snake game with a proper main
menu, difficulty levels, power-ups, obstacles, sound, achievements, and
a stats/save system on top of the core "snake eats food and grows"
gameplay. Everything is written in Python using Pygame, split across
several files using basic OOP (Snake, Food, Obstacle, PowerUp, Button/
Menu, etc. each get their own class).

I tried to keep the code readable rather than "clever" - there's a few
spots where I know a more experienced dev would probably structure
things differently (noted some of those in Future Improvements below),
but everything works and I understand every line of it, which felt more
important than making it look fancy.

## Features

**Core**
- Classic arrow key / WASD movement
- Food spawns randomly, snake grows when it eats
- Live score display
- Game over screen showing your final score
- Restart without closing the game
- Pause / resume with `P`

**Extra stuff I added**
- Main menu (Start, Instructions, Settings, Statistics, Exit)
- 3 difficulty levels (Easy / Medium / Hard) that control base speed
- Speed gradually increases as your score goes up
- High score saved to a local text file so it persists between runs
- Sound effects for eating food, eating bonus food, and game over
- Background music with a mute toggle (`M`)
- Obstacles that start appearing once you pass score milestones
- Bonus food that shows up occasionally, is worth more, and disappears
  if you don't grab it fast enough (it blinks faster as a warning)
- 4 snake color themes, pick one in Settings
- 3-2-1 countdown before each run starts
- Particle burst effect when you eat something
- Power-ups: Slow Motion, Double Points, and a one-hit Shield
- Statistics screen (high score, games played, average score, total food eaten)
- Achievement system (First Bite, Half Century, Century Club, Survivor)
- Progress (stats + achievements) saved to a json file so it's there next time you open the game
- Day / Night display mode toggle
- 3 selectable board sizes (Small / Medium / Large)
- Animated floating shapes in the menu background, just for some life
- In-game keyboard shortcut list (in the Instructions screen)

## Installation

You need Python 3.8+ installed.

```bash
# 1. unzip / clone the project, then cd into it
cd snake_game

# 2. (optional but recommended) make a virtual environment
python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate

# 3. install the one dependency
pip install -r requirements.txt

# 4. run it
python main.py
```

If you don't hear any sound, it's probably because the placeholder wav
files weren't generated. Run `python make_sounds.py` once and it'll
create them in `assets/sounds` and `assets/music` (see the note in that
file - I made these with a small script instead of downloading sound
packs).

## Controls

| Key | Action |
|---|---|
| Arrow Keys / WASD | Move the snake |
| P | Pause / Resume |
| M | Mute / Unmute sound |
| Esc | Back to main menu |
| Enter | Restart after Game Over |
| Mouse | Click buttons in menus |

## Folder Structure

```
snake_game/
├── main.py                # entry point - run this
├── game.py                # Game class, the main state machine + loop
├── snake.py                # Snake class
├── food.py                 # Food + BonusFood classes
├── obstacle.py              # Obstacle class
├── powerup.py               # PowerUp class
├── particle.py               # Particle / ParticleSystem / FloatingShape (menu bg)
├── button.py                 # Button + Menu classes (UI)
├── achievements.py            # AchievementManager class
├── stats_manager.py            # StatsManager class (save/load progress.json)
├── settings.py                  # all constants / colors / config in one place
├── make_sounds.py                # one-off script that generates the placeholder sfx
├── requirements.txt
├── README.md
├── assets/
│   ├── sounds/
│   │   ├── eat.wav
│   │   ├── bonus.wav
│   │   └── gameover.wav
│   └── music/
│       └── background.wav
└── data/                          # created automatically the first time you run the game
    ├── highscore.txt              # just a single number
    └── progress.json              # stats + achievements
```

## How It Works (step by step)

1. **`main.py`** creates one `Game` object and calls `game.run()`. That's it.

2. **`Game.__init__`** sets up pygame, loads sounds, loads the saved
   high score / stats / achievements from disk, builds all the menu
   buttons, and sets the starting state to `"MENU"`.

3. The game runs as a **state machine** - `self.state` is a string like
   `"MENU"`, `"PLAYING"`, `"PAUSED"`, `"GAMEOVER"` etc, and the main loop
   just checks what state we're in to decide what to update/draw that
   frame. Switching states is just setting `self.state = "..."`.

4. **Main loop** (`Game.run`) does the classic three things every frame:
   handle input -> update game logic -> draw everything -> flip the
   display. `self.clock.tick(60)` keeps it at 60fps.

5. **Snake movement is on its own timer**, separate from the 60fps loop.
   If movement was tied directly to the frame rate the snake would zoom
   across the screen on a fast computer and crawl on a slow one. Instead
   `Game._update_playing` adds up the milliseconds that have passed
   (`dt`) into `self.move_timer`, and only actually moves the snake once
   enough time has passed (`move_interval`, which gets smaller as your
   score goes up = faster snake).

6. **Collisions** are checked right after the snake moves
   (`Game._step_snake`): wall, self, and obstacles. If a `Shield`
   power-up is active it absorbs ONE of these hits instead of ending
   the game. Otherwise it's game over.

7. **Food / bonus food / power-ups** are just objects sitting at a grid
   position that get checked against the snake's head position every
   move. If they match, the relevant `_eat_...` / `_collect_powerup`
   method runs (adds score, particles, sound, etc).

8. **Obstacles** get added in pairs every time your score crosses a
   multiple of 40 (`Obstacle.maybe_add_blocks`), so the board slowly
   gets harder instead of starting hard.

9. When the snake dies, `Game._game_over()` saves the high score (if it
   beat the old one), updates the stats file, checks achievements one
   last time, and switches to the `"GAMEOVER"` state which shows the
   final score and a restart button.

10. Settings (theme, board size, day/night, mute) live as plain
    attributes on the `Game` object and get changed directly by button
    clicks in the Settings menu - they're not saved between sessions
    right now (see Future Improvements).

## Future Improvements

Things I'd add if I had more time (or for a v2):

- Save the chosen settings (theme/board size/day-night/mute) between
  sessions instead of resetting to defaults every time you open the game
- Online or local multiplayer (split screen, two snakes)
- Smoother per-pixel movement animation instead of snapping grid-to-grid
- A proper leaderboard with player names instead of just one high score number
- More obstacle patterns/shapes instead of single random blocks
- Replace the placeholder beep sounds with actual sound design / real music
- More power-up types (speed boost, score multiplier stacking, etc)
- An actual settings.json so settings persist
- Controller / gamepad support
- Mobile touch controls if this ever got ported

## Notes

This was built and tested on Python 3.12 with Pygame 2.6.1, should work
fine on anything Python 3.8+. If pygame fails to install, make sure pip
is up to date (`pip install --upgrade pip`) and try again.
