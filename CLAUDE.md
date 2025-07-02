# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Workout Snacks is a Python-based progressive exercise tracking application that encourages regular micro-workouts with equipment-based exercise progressions. The focus is on form over speed, with a streamlined workflow for mobile/remote workouts.

## Key Components

- **workout_cli.py**: Simplified CLI application (database-driven, no hardcoded exercises)
- **populate_exercises.py**: Equipment-based exercise database setup script
- **workout.sh**: Shell script runner with virtual environment support
- **SQLite Database**: Stores exercises, workout sessions, and progress in ~/.workout-snacks/

## Core Philosophy

- **Form over speed**: No timers, focus on proper form and personal limits
- **Equipment-aware**: Exercises adapt to available equipment (bodyweight, pull-up bar, dumbbells, barbell, treadmill)
- **Progressive difficulty**: Automatically scales when achieving 15+ reps
- **Mobile-friendly**: Shows all 4 exercises upfront for photo and remote execution
- **Database-driven**: All exercises loaded from SQLite, no hardcoded data

## Development Commands

### First-Time Setup

```bash
# Setup personalized exercise database
python populate_exercises.py
```

This interactive script asks about available equipment and populates the database with appropriate exercise progressions.

### Daily Usage

```bash
# Using shell script (recommended)
./workout.sh workout        # Start workout session
./workout.sh progress       # View progress and stats

# Direct python execution
python workout_cli.py workout     # Start workout
python workout_cli.py progress    # View progress
```

### Development Dependencies

```bash
# Minimal dependencies (all in Python standard library except collections)
# No external dependencies required for core functionality
```

## Architecture Notes

### Database Schema

- **exercises**: category, name, difficulty_level, max_reps_achieved, description, equipment_required
- **workout_sessions**: timestamp, duration_minutes
- **workout_exercises**: session_id, exercise_name, reps_completed

### Exercise Categories

Current categories with varying difficulty levels (1-13):
- **pushups**: Wall pushups → Planche pushups (9-13 levels depending on equipment)
- **squats**: Chair squats → Dragon squats (9-12 levels)
- **pullups**: Dead hangs → One-arm pull-ups (requires pull-up bar, 9-13 levels)
- **core**: Dead bugs → Human flag (8-12 levels)
- **dips**: Assisted dips → Impossible dips (requires pull-up bar, 6-10 levels)
- **cardio**: Marching → Devil press (6-11 levels depending on equipment)
- **yoga**: Child's pose → Scorpion pose (12 levels, bodyweight only)
- **stretches**: Neck rolls → Spinal twist (12 levels, bodyweight only)

### Workout Logic

1. **Exercise Selection**: Selects 4 exercises from different categories randomly
2. **Progression Logic**: 
   - If max_reps_achieved == 0: Start with current exercise
   - If max_reps_achieved >= 15: Progress to next difficulty level
   - Otherwise: Stay at current level
3. **Display**: Shows current level and previous level for context
4. **Input**: User enters reps completed (no timer pressure)
5. **Tracking**: Updates personal bests and progression automatically

## File Structure

```
workout-snacks/
├── workout_cli.py           # Main CLI application (cleaned, database-driven)
├── populate_exercises.py    # Exercise database setup (equipment-based)
├── workout.sh              # Shell script runner (.venv support)
├── README.md               # User documentation
├── CLAUDE.md               # This file (development guidance)
└── ~/.workout-snacks/
    └── workout_data.db     # SQLite database (auto-created)
```

## User Experience

The application provides a streamlined workflow:

1. **Setup**: Run `populate_exercises.py` once to configure exercises based on equipment
2. **Workout**: Run `./workout.sh workout` to see 4 exercises, take photo if needed, do workout, enter reps
3. **Progress**: Run `./workout.sh progress` to see current level in each exercise lane and recent activity

### Key Design Decisions

- **No timers**: Removed all timer functionality to focus on form over speed
- **Equipment-aware**: Database populated based on user's available equipment
- **Mobile workflow**: All exercises shown upfront for photo capture and remote execution
- **Simplified progress**: Shows only essential info (current level, recent activity)
- **Database-first**: Eliminated hardcoded exercise data, everything comes from database

## Important Implementation Notes

- **No hardcoded exercises**: All exercise data comes from database populated by `populate_exercises.py`
- **Equipment filtering**: Exercises are filtered during database population, not at runtime
- **Single source of truth**: Database is the only source for exercises, no duplication
- **Graceful degradation**: Handles missing database with helpful error messages
- **Clean separation**: Setup (populate_exercises.py) vs. usage (workout_cli.py)

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.