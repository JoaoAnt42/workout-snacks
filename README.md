# Workout Snacks

A Python-based progressive exercise tracking application that provides timed workout reminders and tracks exercise progression. Encourages regular micro-workouts (1-5 minutes) throughout the day with automatic difficulty scaling.

## Features

### ✅ Completed Goals
- **90-minute notification system** with sound alerts
- **30-minute warning system** with tray icon changes for early workout initiation
- **3-exercise workout sessions** with 1-minute intervals per exercise
- **Progressive difficulty scaling** - automatically increases when achieving 15+ reps
- **Multiple interfaces**: GUI with system tray, CLI, and desktop timer versions
- **Comprehensive tracking** with SQLite database and performance charts
- **Linux integration** with Waybar support for Wayland/Hyprland environments

### Core Components
- **6 exercise categories**: pushups, squats, pullups, core, dips, cardio
- **9 difficulty levels** per category (54 total exercise variations)
- **Real-time progress tracking** with personal best records
- **Data visualization** with matplotlib charts
- **Cross-platform notifications** using plyer

## Quick Start

### Installation
```bash
pip install plyer pystray pillow apscheduler matplotlib
# For GUI support: sudo pacman -S tk (Arch) or sudo apt install python3-tk (Ubuntu)
```

### Usage
```bash
python main.py                    # GUI with system tray
python workout_cli.py             # CLI version
python workout_gui.py             # Desktop GUI with timer
python workout_waybar.py daemon   # Waybar integration (recommended for Hyprland)
```

### CLI Commands
```bash
python workout_cli.py workout     # Start workout session
python workout_cli.py progress    # View progress and stats  
python workout_cli.py charts      # Show visualization charts
python workout_cli.py daemon      # Background notifications only
```

## System Integration

### Hyprland/Wayland Users
Add to your autostart.conf:
```bash
exec-once = cd /path/to/workout-snacks && python workout_waybar.py daemon &
```

Then add the custom module from `waybar-workout-config.json` to your waybar configuration.

## Architecture

- **Progressive System**: Tracks maximum reps per exercise; advances difficulty at 15+ reps threshold
- **Data Persistence**: SQLite database stores workout sessions, exercise progress, and personal bests
- **Notification Scheduling**: APScheduler manages 90-minute intervals with 30-minute warnings
- **Multi-Interface Design**: Separate modules for GUI, CLI, and system integration

## Baseline Configuration

Pre-configured for intermediate fitness level:
- 15 single-arm pushups (wide stance)
- 20 air squats
- 10 pull-ups

The system automatically adapts difficulty based on your performance, ensuring continuous progression without manual adjustment.
