#!/usr/bin/env python3
"""
Workout Snacks CLI - Command line version without system tray
"""

import argparse
import random
import sqlite3
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class Exercise:
    name: str
    difficulty_level: int
    max_reps_achieved: int = 0
    description: str = ""
    category: str = ""


@dataclass
class WorkoutSession:
    timestamp: datetime
    exercises: List[Tuple[str, int]]  # (exercise_name, reps_completed)


class WorkoutApp:
    def __init__(self):
        self.data_dir = Path.home() / ".workout-snacks"
        self.data_dir.mkdir(exist_ok=True)
        self.db_file = self.data_dir / "workout_data.db"

        self.exercises: Dict[str, List[Exercise]] = {}
        self.workout_history: List[WorkoutSession] = []

        self.init_database()
        self.load_data()

    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        # Create exercises table with equipment field
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                name TEXT NOT NULL,
                difficulty_level INTEGER NOT NULL,
                max_reps_achieved INTEGER DEFAULT 0,
                description TEXT,
                equipment_required TEXT,
                UNIQUE(category, name)
            )
        """)

        # Create workout_sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workout_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                duration_minutes INTEGER DEFAULT 3
            )
        """)

        # Create workout_exercises table (many-to-many)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workout_exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                exercise_name TEXT NOT NULL,
                reps_completed INTEGER NOT NULL,
                FOREIGN KEY (session_id) REFERENCES workout_sessions (id)
            )
        """)

        conn.commit()
        conn.close()

    def load_data(self):
        """Load workout history and exercise progress from database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        # Load exercises from database
        try:
            cursor.execute("""
                SELECT category, name, difficulty_level, max_reps_achieved, description 
                FROM exercises 
                ORDER BY category, difficulty_level
            """)

            for (
                category,
                name,
                difficulty_level,
                max_reps,
                description,
            ) in cursor.fetchall():
                if category not in self.exercises:
                    self.exercises[category] = []

                exercise = Exercise(
                    name=name,
                    difficulty_level=difficulty_level,
                    max_reps_achieved=max_reps,
                    description=description or "",
                    category=category,
                )
                self.exercises[category].append(exercise)

        except sqlite3.OperationalError:
            print("No exercises found in database.")
            print(
                "Please run 'python populate_exercises.py' to set up your exercise database."
            )
            return

        # Load workout history
        cursor.execute("""
            SELECT ws.timestamp, ws.duration_minutes, we.exercise_name, we.reps_completed
            FROM workout_sessions ws
            JOIN workout_exercises we ON ws.id = we.session_id
            ORDER BY ws.timestamp
        """)

        sessions_data = {}
        for timestamp, duration, exercise_name, reps in cursor.fetchall():
            if timestamp not in sessions_data:
                sessions_data[timestamp] = {"duration": duration, "exercises": []}
            sessions_data[timestamp]["exercises"].append((exercise_name, reps))

        for timestamp, data in sessions_data.items():
            session = WorkoutSession(
                timestamp=datetime.fromisoformat(timestamp),
                exercises=data["exercises"],
            )
            self.workout_history.append(session)

        conn.close()

    def save_data(self):
        """Save exercise progress to database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        # Update exercise progress
        for category, exercises in self.exercises.items():
            for exercise in exercises:
                cursor.execute(
                    """
                    UPDATE exercises 
                    SET max_reps_achieved = ? 
                    WHERE category = ? AND name = ?
                """,
                    (exercise.max_reps_achieved, category, exercise.name),
                )

        conn.commit()
        conn.close()

    def save_workout_session(self, session: WorkoutSession):
        """Save a workout session to database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        # Insert workout session
        cursor.execute(
            """
            INSERT INTO workout_sessions (timestamp, duration_minutes) 
            VALUES (?, ?)
        """,
            (session.timestamp.isoformat(), 3),
        )

        session_id = cursor.lastrowid

        # Insert workout exercises
        for exercise_name, reps in session.exercises:
            cursor.execute(
                """
                INSERT INTO workout_exercises (session_id, exercise_name, reps_completed) 
                VALUES (?, ?, ?)
            """,
                (session_id, exercise_name, reps),
            )

        conn.commit()
        conn.close()

    def get_current_exercises(self) -> List[Exercise]:
        """Get 4 exercises for current workout based on progression"""
        if not self.exercises:
            print("No exercises available. Run 'python populate_exercises.py' first.")
            return []

        # Get one exercise from 4 different categories
        available_categories = list(self.exercises.keys())
        selected_categories = random.sample(
            available_categories, min(4, len(available_categories))
        )

        workout_exercises = []

        for category in selected_categories:
            exercises = self.exercises[category]
            current_exercise = exercises[0]  # Start with easiest

            # Find the appropriate difficulty level based on progression
            for exercise in exercises:
                if exercise.max_reps_achieved == 0:
                    # Never done this exercise, start here
                    current_exercise = exercise
                    break
                if exercise.max_reps_achieved >= 15:  # Progression threshold
                    # Look for next level
                    next_level_exercises = [
                        e
                        for e in exercises
                        if e.difficulty_level == exercise.difficulty_level + 1
                    ]
                    if next_level_exercises:
                        current_exercise = next_level_exercises[0]
                    else:
                        current_exercise = exercise  # Stay at current level
                else:
                    current_exercise = exercise
                    break

            workout_exercises.append(current_exercise)

        return workout_exercises

    def get_exercise_progression_info(self, exercise: Exercise, category: str) -> tuple:
        """Get current and previous level exercise info for display"""
        exercises_in_category = self.exercises[category]
        previous_exercise = None

        # Find previous level exercise
        for ex in exercises_in_category:
            if ex.difficulty_level == exercise.difficulty_level - 1:
                previous_exercise = ex
                break

        return exercise, previous_exercise

    def get_last_workout_time(self) -> str:
        """Get timestamp of last workout session"""
        if not self.workout_history:
            return "No previous workouts found"

        last_workout = max(self.workout_history, key=lambda x: x.timestamp)
        return last_workout.timestamp.strftime("%Y-%m-%d %H:%M:%S")

    def get_current_level_for_category(self, category: str) -> Exercise:
        """Get the current level exercise for a category"""
        if category not in self.exercises:
            return None

        exercises = self.exercises[category]

        # Find the highest level with reps achieved
        current_exercise = exercises[0]  # Default to first

        for exercise in exercises:
            if exercise.max_reps_achieved > 0:
                current_exercise = exercise
            else:
                break  # First exercise with no reps is current level

        return current_exercise

    def get_last_5_days_workout_count(self) -> dict:
        """Get workout count for last 5 days"""
        today = datetime.now().date()
        last_5_days = [(today - timedelta(days=i)) for i in range(5)]

        # Count workouts per day
        workout_dates = [session.timestamp.date() for session in self.workout_history]
        date_counts = Counter(workout_dates)

        daily_counts = {}
        for day in last_5_days:
            daily_counts[day] = date_counts.get(day, 0)

        return daily_counts

    def start_workout(self):
        """Start a workout session"""
        exercises = self.get_current_exercises()

        if not exercises:
            return

        print("\n" + "=" * 60)
        print("🏋️  WORKOUT TIME! 🏋️")
        print("=" * 60)
        print(f"Last workout: {self.get_last_workout_time()}")
        print("\nToday's 4 exercises (do as many reps as you can with good form):")
        print()

        # Display all 4 exercises upfront
        for i, exercise in enumerate(exercises, 1):
            category = exercise.category
            if category:
                _, previous_ex = self.get_exercise_progression_info(exercise, category)
            else:
                previous_ex = None

            print(f"{i}. {exercise.name} (Level {exercise.difficulty_level})")
            print(f"   Description: {exercise.description}")
            print(f"   Personal Best: {exercise.max_reps_achieved} reps")
            if previous_ex:
                print(
                    f"   Previous Level: {previous_ex.name} (Level {previous_ex.difficulty_level})"
                )
            print()

        print("📸 Take a photo if needed, then do your workout!")
        print("\nWhen ready, enter your completed reps for each exercise:")
        print()

        completed_exercises = []

        for i, exercise in enumerate(exercises, 1):
            print(f"{i}. {exercise.name}:")

            # Get user input for reps completed
            while True:
                try:
                    reps = int(input("   How many reps did you complete? "))
                    if reps >= 0:
                        break
                    print("   Please enter a non-negative number.")
                except ValueError:
                    print("   Please enter a valid number.")

            completed_exercises.append((exercise.name, reps))

            # Update personal best
            if reps > exercise.max_reps_achieved:
                exercise.max_reps_achieved = reps
                print(f"   🎉 New personal best! ({reps} reps)")
            elif reps >= 15 and exercise.difficulty_level < 20:  # Check for progression
                print("   💪 Great job! You're ready to progress to the next level!")

            print()

        # Save workout session
        session = WorkoutSession(
            timestamp=datetime.now(), exercises=completed_exercises
        )
        self.workout_history.append(session)
        self.save_workout_session(session)
        self.save_data()

        print("Great job! Workout completed. 💪")
        print("=" * 60)

    def show_progress(self):
        """Display simplified workout progress"""
        if not self.exercises:
            print(
                "No exercises found. Run 'python populate_exercises.py' to set up your exercise database."
            )
            return

        print("\n" + "=" * 50)
        print("📊 WORKOUT PROGRESS 📊")
        print("=" * 50)

        # Show current level for each exercise lane
        print("Current Level in Each Exercise Lane:")
        print()

        for category, exercises in self.exercises.items():
            current_exercise = self.get_current_level_for_category(category)
            if current_exercise:
                max_level = max(ex.difficulty_level for ex in exercises)

                print(f"{category.upper()}:")
                print(
                    f"  Current: {current_exercise.name} (Level {current_exercise.difficulty_level}/{max_level})"
                )
                print(f"  Best: {current_exercise.max_reps_achieved} reps")
                print()

        # Show last 5 days workout count
        print("Workouts in Last 5 Days:")
        daily_counts = self.get_last_5_days_workout_count()

        for day, count in daily_counts.items():
            day_name = day.strftime("%a %m-%d")
            print(f"  {day_name}: {count} workouts")

        total_recent = sum(daily_counts.values())
        print(f"\nTotal last 5 days: {total_recent} workouts")
        print(f"Total all time: {len(self.workout_history)} workouts")
        print("=" * 50)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Workout Snacks - Calisthenics Tracker"
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=["workout", "progress"],
        help="Command to execute",
    )

    args = parser.parse_args()
    app = WorkoutApp()

    if args.command == "workout":
        app.start_workout()
    elif args.command == "progress":
        app.show_progress()
    else:
        print("🏋️  Workout Snacks CLI 🏋️")
        print("Usage:")
        print("  python workout_cli.py workout   - Start a workout session")
        print("  python workout_cli.py progress  - View progress and stats")


if __name__ == "__main__":
    main()