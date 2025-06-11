# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Workout Snacks is a Python-based progressive exercise tracking application that provides timed workout reminders and tracks exercise progression. The goal is to encourage regular micro-workouts (1-5 minutes) throughout the day with progressive difficulty scaling.

## Key Components

- **main.py**: Full-featured GUI application with system tray integration using pystray
- **workout_cli.py**: Command-line interface version without GUI dependencies
- **workout_gui.py**: Desktop GUI application with built-in 1-minute timer for PC workouts
- **ExerciseDatabase**: Manages 6 exercise categories (pushups, squats, pullups, core, dips, cardio) with 9 difficulty levels each
- **SQLite Database**: Stores workout sessions, exercise progress, and personal bests in ~/.workout-snacks/
- **Progressive Difficulty**: Automatically increases exercise difficulty when user achieves 15+ reps

## Development Commands

### Run the Application
```bash
python main.py                    # GUI version with system tray
python workout_cli.py             # CLI version
python workout_gui.py             # Desktop GUI with timer
```

### Hyprland System Tray
pystray doesn't work well with Wayland/Hyprland. Use these alternatives:

**Option 1: Waybar Integration (Recommended)**
```bash
python workout_waybar.py daemon    # Start waybar-compatible daemon
```
Add the custom module from `waybar-workout-config.json` to your waybar config.

**Option 2: CLI Daemon**
```bash
python workout_cli.py daemon       # Notifications only
```

### Autostart with Hyprland
Add to your autostart.conf:
```bash
exec-once = cd /home/joaoant/Documents/workout-snacks && python workout_waybar.py daemon &
```

### CLI Commands
```bash
python workout_cli.py workout     # Start workout session
python workout_cli.py progress    # View progress and stats  
python workout_cli.py charts      # Show visualization charts
python workout_cli.py daemon      # Background notifications
```

### Install Dependencies
```bash
pip install plyer pystray pillow apscheduler matplotlib
# or
uv pip install plyer pystray pillow apscheduler matplotlib

# For GUI version, also install tkinter:
sudo pacman -S tk                 # Arch Linux
sudo apt install python3-tk      # Ubuntu/Debian
sudo dnf install tkinter          # Fedora
```

## Architecture Notes

- **Workout Logic**: Selects 3 exercises from different categories, each for 1 minute
- **Progression System**: Tracks max reps achieved per exercise; advances difficulty at 15+ reps
- **Data Persistence**: SQLite database with tables for exercises, workout_sessions, and workout_exercises
- **Notifications**: 90-minute intervals with 30-minute warnings (GUI version)
- **Baseline Levels**: Pre-configured for user's current ability (15 single-arm pushups, 20 air squats, 10 pull-ups)

## User Experience

The app provides both immediate feedback during workouts and long-term progress tracking through charts and statistics. Exercise difficulty automatically progresses based on performance, ensuring continuous challenge without manual adjustment.