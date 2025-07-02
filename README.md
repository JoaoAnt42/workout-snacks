# Workout Snacks

A Python-based progressive exercise tracking application that encourages regular micro-workouts throughout the day with automatic difficulty scaling. Focus on form over speed with equipment-based exercise progressions.

## Features

### ✅ Core Functionality

- **4-exercise workout sessions** without timer - focus on form over speed
- **Equipment-based exercise selection** (bodyweight, pull-up bar, dumbbells, barbell, treadmill)
- **Progressive difficulty scaling** - automatically increases when achieving 15+ reps
- **Multiple exercise categories**: pushups, squats, pullups, core, dips, cardio, yoga, stretches
- **Comprehensive tracking** with SQLite database and simplified progress display
- **Photo-friendly workflow** - see all exercises upfront for mobile workouts

### Exercise Categories

- **8+ exercise categories** with varying difficulty levels (up to 13 levels per category)
- **Equipment-aware progressions** that adapt to your available equipment
- **Extensive variations**: From basic bodyweight to advanced calisthenics
- **Real-time progress tracking** with personal best records

## Quick Start

### 1. Setup Exercise Database

```bash
python populate_exercises.py
```

This will ask about your available equipment and create a personalized exercise database.

### 2. Installation

```bash
# Minimal dependencies for CLI version
pip install sqlite3
# or with uv:
uv pip install python-dateutil
```

### 3. Usage

```bash
# Using the shell script (recommended)
./workout.sh workout     # Start workout session
./workout.sh progress    # View progress and stats

# Or directly with python
python workout_cli.py workout     # Start workout session
python workout_cli.py progress    # View progress and stats
```

## Workflow

### First Time Setup

1. **Setup exercises**: `python populate_exercises.py`
   - Select your available equipment (pull-up bar, dumbbells, barbell, treadmill)
   - Creates personalized exercise database with appropriate progressions
2. **Start working out**: `./workout.sh workout`
   - Shows 4 exercises with current level and previous level
   - Take a photo if needed, then do the workout
   - Enter reps completed for each exercise
   - Automatic progression tracking

### Regular Use

- **View progress**: `./workout.sh progress`
  - Current level in each exercise lane
  - Workout count for last 5 days
  - Total workout statistics

## Exercise Categories

### Equipment-Based Categories

- **Bodyweight**: Available to everyone (pushups, squats, core, cardio, yoga, stretches)
- **Pull-up bar**: Enhanced upper body progressions (pullups, dips, hanging core exercises)
- **Dumbbells**: Weighted variations and strength training progressions
- **Barbell**: Advanced strength training (squats, deadlifts, presses)
- **Treadmill**: Cardio progressions from walking to sprint intervals

### Progression Examples

- **Pushups**: Wall pushups → Regular pushups → Handstand pushups → Planche pushups
- **Squats**: Chair squats → Pistol squats → Shrimp squats
- **Yoga**: Child's pose → Sun salutations → Advanced poses like Scorpion
- **Core**: Crunches → Planks → L-sits → Dragon flags → Human flag

## Architecture

- **Database-Driven**: All exercises loaded from SQLite database
- **Equipment-Aware**: Exercises filtered based on available equipment
- **Progressive System**: Tracks maximum reps per exercise; advances at 15+ reps threshold
- **Form-Focused**: No timer pressure - emphasizes proper form and personal limits
- **Mobile-Friendly**: Display all exercises upfront for photo and remote execution

The system automatically adapts difficulty based on your performance, ensuring continuous progression without manual adjustment while respecting your equipment limitations.

## Files Structure

- `workout_cli.py` - Main workout application (cleaned and simplified)
- `populate_exercises.py` - Equipment-based exercise database setup
- `workout.sh` - Shell script runner with virtual environment support
- `CLAUDE.md` - Development guidance and project overview
