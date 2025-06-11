#!/usr/bin/env python3
"""
Workout Snacks - A progressive exercise notification app
"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple

try:
    from collections import Counter, defaultdict

    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt
    import pystray
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    from PIL import Image, ImageDraw
    from plyer import notification
    from pystray import Menu, MenuItem
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Run: pip install plyer pystray pillow apscheduler matplotlib")
    exit(1)


@dataclass
class Exercise:
    name: str
    difficulty_level: int
    max_reps_achieved: int = 0
    description: str = ""


@dataclass
class WorkoutSession:
    timestamp: datetime
    exercises: List[Tuple[str, int]]  # (exercise_name, reps_completed)
    duration_minutes: int = 3


class ExerciseDatabase:
    def __init__(self):
        self.exercises = {
            "pushups": [
                Exercise("Knee Push-ups", 1, description="Push-ups on knees"),
                Exercise("Regular Push-ups", 2, description="Standard push-ups"),
                Exercise("Wide Push-ups", 3, description="Hands wider than shoulders"),
                Exercise("Diamond Push-ups", 4, description="Hands in diamond shape"),
                Exercise("Decline Push-ups", 5, description="Feet elevated"),
                Exercise("Pike Push-ups", 6, description="Inverted V position"),
                Exercise("Archer Push-ups", 7, description="One-sided push-ups"),
                Exercise("Single Arm Push-ups", 8, description="One arm push-ups"),
                Exercise(
                    "Planche Push-ups", 9, description="Advanced planche position"
                ),
            ],
            "squats": [
                Exercise("Chair Squats", 1, description="Assisted squats with chair"),
                Exercise("Air Squats", 2, description="Bodyweight squats"),
                Exercise("Sumo Squats", 3, description="Wide stance squats"),
                Exercise("Jump Squats", 4, description="Explosive squat jumps"),
                Exercise("Bulgarian Split Squats", 5, description="Rear foot elevated"),
                Exercise("Cossack Squats", 6, description="Side-to-side squats"),
                Exercise("Single Leg Squats", 7, description="Pistol squats"),
                Exercise(
                    "Jump Pistol Squats", 8, description="Explosive pistol squats"
                ),
                Exercise("Shrimp Squats", 9, description="Advanced single leg squat"),
            ],
            "pullups": [
                Exercise("Dead Hangs", 1, description="Hanging from bar"),
                Exercise("Negative Pull-ups", 2, description="Slow descent from top"),
                Exercise(
                    "Assisted Pull-ups", 3, description="Band or partner assisted"
                ),
                Exercise("Regular Pull-ups", 4, description="Standard pull-ups"),
                Exercise("Wide Grip Pull-ups", 5, description="Wide grip variation"),
                Exercise("Chin-ups", 6, description="Underhand grip"),
                Exercise("Commando Pull-ups", 7, description="Side-to-side pull-ups"),
                Exercise("Weighted Pull-ups", 8, description="Add weight"),
                Exercise("Muscle-ups", 9, description="Pull-up to dip transition"),
            ],
            "core": [
                Exercise("Crunches", 1, description="Basic abdominal crunches"),
                Exercise("Plank", 2, description="Hold plank position (seconds)"),
                Exercise(
                    "Bicycle Crunches", 3, description="Alternating elbow to knee"
                ),
                Exercise("Russian Twists", 4, description="Seated twisting motion"),
                Exercise(
                    "Mountain Climbers", 5, description="Running in plank position"
                ),
                Exercise("Hollow Body Hold", 6, description="Hollow position hold"),
                Exercise("L-sits", 7, description="Legs at 90 degrees"),
                Exercise("Dragon Flags", 8, description="Advanced core exercise"),
                Exercise("Human Flag", 9, description="Side plank on pole"),
            ],
            "dips": [
                Exercise("Assisted Dips", 1, description="Band or partner assisted"),
                Exercise("Bench Dips", 2, description="Feet on ground"),
                Exercise("Elevated Bench Dips", 3, description="Feet elevated"),
                Exercise("Parallel Bar Dips", 4, description="Standard dips"),
                Exercise("Ring Dips", 5, description="On gymnastic rings"),
                Exercise("Weighted Dips", 6, description="Add weight"),
                Exercise("Archer Dips", 7, description="One-sided dips"),
                Exercise("Single Bar Dips", 8, description="On single bar"),
                Exercise("Impossible Dips", 9, description="Advanced ring dips"),
            ],
            "cardio": [
                Exercise("Jumping Jacks", 1, description="Basic jumping jacks"),
                Exercise("High Knees", 2, description="Running in place"),
                Exercise("Burpees", 3, description="Full body exercise"),
                Exercise("Mountain Climbers", 4, description="Fast mountain climbers"),
                Exercise("Star Jumps", 5, description="Explosive star position"),
                Exercise("Tuck Jumps", 6, description="Knees to chest jumps"),
                Exercise("Squat Jumps", 7, description="Continuous squat jumps"),
                Exercise("Burpee Box Jumps", 8, description="Burpee with box jump"),
                Exercise("Devil Press", 9, description="Burpee with dumbbells"),
            ],
        }

        # Set baseline levels based on user's current ability
        self.exercises["pushups"][7].max_reps_achieved = 15  # Single arm
        self.exercises["squats"][1].max_reps_achieved = 20  # Air squats
        self.exercises["pullups"][3].max_reps_achieved = 10  # Pull-ups


class WorkoutSnacksApp:
    def __init__(self):
        self.data_dir = Path.home() / ".workout-snacks"
        self.data_dir.mkdir(exist_ok=True)
        self.db_file = self.data_dir / "workout_data.db"

        self.exercise_db = ExerciseDatabase()
        self.workout_history: List[WorkoutSession] = []
        self.scheduler = BackgroundScheduler()
        self.tray_icon = None
        self.next_workout_time = None
        self.warning_shown = False

        self.init_database()
        self.load_data()

    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        # Create exercises table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                name TEXT NOT NULL,
                difficulty_level INTEGER NOT NULL,
                max_reps_achieved INTEGER DEFAULT 0,
                description TEXT,
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

        # Populate initial exercise data
        self.populate_initial_exercises()

    def populate_initial_exercises(self):
        """Populate database with initial exercise data"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        for category, exercises in self.exercise_db.exercises.items():
            for exercise in exercises:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO exercises 
                    (category, name, difficulty_level, max_reps_achieved, description) 
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        category,
                        exercise.name,
                        exercise.difficulty_level,
                        exercise.max_reps_achieved,
                        exercise.description,
                    ),
                )

        conn.commit()
        conn.close()

    def load_data(self):
        """Load workout history and exercise progress from database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        # Load exercise progress
        cursor.execute("SELECT category, name, max_reps_achieved FROM exercises")
        for category, name, max_reps in cursor.fetchall():
            if category in self.exercise_db.exercises:
                for exercise in self.exercise_db.exercises[category]:
                    if exercise.name == name:
                        exercise.max_reps_achieved = max_reps
                        break

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
                duration_minutes=data["duration"],
            )
            self.workout_history.append(session)

        conn.close()

    def save_data(self):
        """Save exercise progress to database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        # Update exercise progress
        for category, exercises in self.exercise_db.exercises.items():
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
            (session.timestamp.isoformat(), session.duration_minutes),
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
        """Get 3 exercises for current workout based on progression"""
        import random

        # Get one exercise from 3 different categories
        available_categories = list(self.exercise_db.exercises.keys())
        selected_categories = random.sample(
            available_categories, min(3, len(available_categories))
        )

        workout_exercises = []

        for category in selected_categories:
            exercises = self.exercise_db.exercises[category]
            current_exercise = exercises[0]  # Start with easiest

            # Find the appropriate difficulty level based on progression
            for exercise in exercises:
                if exercise.max_reps_achieved == 0:
                    # Never done this exercise, start here
                    current_exercise = exercise
                    break
                elif (
                    exercise.max_reps_achieved >= 15
                ):  # Lower threshold for progression
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

    def create_tray_icon(self, warning_mode=False):
        """Create system tray icon"""
        # Create a more visible icon for Hyprland
        image = Image.new("RGBA", (64, 64), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw a filled circle with border
        if warning_mode:
            draw.ellipse([8, 8, 56, 56], fill=(255, 100, 100, 255), outline=(200, 0, 0, 255), width=3)
        else:
            draw.ellipse([8, 8, 56, 56], fill=(100, 255, 100, 255), outline=(0, 200, 0, 255), width=3)
        
        # Add "W" for workout
        draw.text((22, 18), "W", fill=(0, 0, 0, 255), anchor="mm")

        menu = Menu(
            MenuItem("Start Workout", self.start_workout),
            MenuItem("View Progress", self.show_progress),
            MenuItem("View Charts", self.show_charts),
            MenuItem("Quit", self.quit_app),
        )

        return pystray.Icon("workout-snacks", image, menu=menu, title="Workout Snacks")

    def start_workout(self, icon=None, item=None):
        """Start a workout session"""
        exercises = self.get_current_exercises()

        print("\n" + "=" * 50)
        print("🏋️  WORKOUT TIME! 🏋️")
        print("=" * 50)
        print("Complete each exercise for 1 minute:")
        print()

        completed_exercises = []

        for i, exercise in enumerate(exercises, 1):
            print(f"{i}. {exercise.name}")
            print(f"   Description: {exercise.description}")
            print(f"   Personal Best: {exercise.max_reps_achieved} reps")
            print()

            # Get user input for reps completed
            while True:
                try:
                    reps = int(
                        input(f"   How many {exercise.name.lower()} did you complete? ")
                    )
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

            print()

        # Save workout session
        session = WorkoutSession(
            timestamp=datetime.now(), exercises=completed_exercises
        )
        self.workout_history.append(session)
        self.save_workout_session(session)
        self.save_data()

        print("Great job! Workout completed. 💪")
        print("Next workout in 90 minutes.")
        print("=" * 50)

        # Reset notification state
        self.warning_shown = False
        self.schedule_next_workout()

        # Update tray icon back to normal
        if self.tray_icon:
            self.tray_icon.icon = self.create_tray_icon(warning_mode=False).icon

    def show_progress(self, icon=None, item=None):
        """Display workout progress"""
        print("\n" + "=" * 50)
        print("📊 WORKOUT PROGRESS 📊")
        print("=" * 50)

        # Show current exercise levels
        print("Current Exercise Levels:")
        for category, exercises in self.exercise_db.exercises.items():
            print(f"\n{category.upper()}:")
            for exercise in exercises:
                status = "✓" if exercise.max_reps_achieved > 0 else "○"
                print(
                    f"  {status} {exercise.name}: {exercise.max_reps_achieved} reps (Level {exercise.difficulty_level})"
                )

        # Show recent workouts
        print(f"\nRecent Workouts ({len(self.workout_history)} total):")
        for session in self.workout_history[-5:]:  # Show last 5
            print(f"  {session.timestamp.strftime('%Y-%m-%d %H:%M')}:")
            for exercise_name, reps in session.exercises:
                print(f"    - {exercise_name}: {reps} reps")

        print("=" * 50)

    def show_charts(self, icon=None, item=None):
        """Display workout visualization charts"""
        if not self.workout_history:
            print("No workout data available for charts.")
            return

        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle("Workout Analytics", fontsize=16, fontweight="bold")

        # Prepare data
        dates = [session.timestamp.date() for session in self.workout_history]
        date_counts = Counter(dates)

        # Chart 1: Workouts per day
        sorted_dates = sorted(date_counts.keys())
        workout_counts = [date_counts[date] for date in sorted_dates]

        ax1.bar(sorted_dates, workout_counts, color="skyblue", alpha=0.7)
        ax1.set_title("Workouts per Day")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Number of Workouts")
        ax1.tick_params(axis="x", rotation=45)

        # Chart 2: Reps per minute trend
        exercise_reps = defaultdict(list)
        exercise_dates = defaultdict(list)

        for session in self.workout_history:
            for exercise_name, reps in session.exercises:
                exercise_reps[exercise_name].append(reps)
                exercise_dates[exercise_name].append(session.timestamp.date())

        # Plot top 3 exercises by frequency
        top_exercises = sorted(
            exercise_reps.keys(), key=lambda x: len(exercise_reps[x]), reverse=True
        )[:3]
        colors = ["red", "green", "blue"]

        for i, exercise in enumerate(top_exercises):
            ax2.plot(
                exercise_dates[exercise],
                exercise_reps[exercise],
                marker="o",
                label=exercise,
                color=colors[i],
                alpha=0.7,
            )

        ax2.set_title("Reps per Minute Trend (Top 3 Exercises)")
        ax2.set_xlabel("Date")
        ax2.set_ylabel("Reps per Minute")
        ax2.legend()
        ax2.tick_params(axis="x", rotation=45)

        # Chart 3: Exercise distribution
        all_exercises = [
            exercise_name
            for session in self.workout_history
            for exercise_name, _ in session.exercises
        ]
        exercise_counts = Counter(all_exercises)

        top_exercises_pie = dict(Counter(all_exercises).most_common(6))
        ax3.pie(
            top_exercises_pie.values(),
            labels=top_exercises_pie.keys(),
            autopct="%1.1f%%",
        )
        ax3.set_title("Exercise Distribution")

        # Chart 4: Personal best progression
        pb_data = {}
        for category, exercises in self.exercise_db.exercises.items():
            for exercise in exercises:
                if exercise.max_reps_achieved > 0:
                    pb_data[f"{exercise.name}"] = exercise.max_reps_achieved

        if pb_data:
            sorted_pb = sorted(pb_data.items(), key=lambda x: x[1], reverse=True)[:8]
            names, values = zip(*sorted_pb)

            ax4.barh(names, values, color="lightgreen", alpha=0.7)
            ax4.set_title("Personal Bests")
            ax4.set_xlabel("Max Reps Achieved")

        plt.tight_layout()
        plt.show()

        # Also show summary stats
        self.show_workout_stats()

    def show_workout_stats(self):
        """Display detailed workout statistics"""
        if not self.workout_history:
            return

        print("\n" + "=" * 50)
        print("📈 DETAILED WORKOUT STATISTICS 📈")
        print("=" * 50)

        # Total workouts
        total_workouts = len(self.workout_history)
        print(f"Total Workouts: {total_workouts}")

        # Workouts per day average
        if total_workouts > 0:
            first_workout = min(
                session.timestamp.date() for session in self.workout_history
            )
            last_workout = max(
                session.timestamp.date() for session in self.workout_history
            )
            days_active = (last_workout - first_workout).days + 1
            avg_per_day = total_workouts / days_active
            print(f"Average Workouts per Day: {avg_per_day:.2f}")

            # Most active day
            dates = [session.timestamp.date() for session in self.workout_history]
            date_counts = Counter(dates)
            most_active_date, max_workouts = date_counts.most_common(1)[0]
            print(f"Most Active Day: {most_active_date} ({max_workouts} workouts)")

            # Exercise statistics
            all_exercises = [
                exercise_name
                for session in self.workout_history
                for exercise_name, _ in session.exercises
            ]
            exercise_counts = Counter(all_exercises)
            print(
                f"\nMost Frequent Exercise: {exercise_counts.most_common(1)[0][0]} ({exercise_counts.most_common(1)[0][1]} times)"
            )

            # Average reps per exercise
            exercise_reps = defaultdict(list)
            for session in self.workout_history:
                for exercise_name, reps in session.exercises:
                    exercise_reps[exercise_name].append(reps)

            print("\nAverage Reps per Exercise:")
            for exercise, reps_list in sorted(exercise_reps.items()):
                avg_reps = sum(reps_list) / len(reps_list)
                print(f"  {exercise}: {avg_reps:.1f} reps")

        print("=" * 50)

    def send_notification(self, title, message, timeout=10):
        """Send desktop notification"""
        try:
            notification.notify(
                title=title, message=message, timeout=timeout, app_name="Workout Snacks"
            )
        except Exception as e:
            print(f"Notification error: {e}")

    def workout_reminder(self):
        """Send workout reminder notification"""
        self.send_notification(
            "Workout Time!",
            "Time for your exercise snack! Click the tray icon to start.",
            timeout=15,
        )
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Workout reminder sent!")

    def workout_warning(self):
        """Show warning 30 minutes before workout"""
        if not self.warning_shown:
            self.send_notification(
                "Workout Coming Up",
                "Exercise break in 30 minutes. Prepare to get moving!",
                timeout=10,
            )

            # Change tray icon to warning mode
            if self.tray_icon:
                self.tray_icon.icon = self.create_tray_icon(warning_mode=True).icon

            self.warning_shown = True
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Workout warning sent!")

    def schedule_next_workout(self):
        """Schedule the next workout and warning"""
        # Clear existing jobs
        self.scheduler.remove_all_jobs()

        # Schedule next workout in 90 minutes
        workout_time = datetime.now() + timedelta(minutes=90)
        warning_time = workout_time - timedelta(minutes=30)

        self.scheduler.add_job(
            self.workout_reminder, "date", run_date=workout_time, id="workout_reminder"
        )

        self.scheduler.add_job(
            self.workout_warning, "date", run_date=warning_time, id="workout_warning"
        )

        self.next_workout_time = workout_time
        print(f"Next workout scheduled for: {workout_time.strftime('%H:%M:%S')}")
        print(f"Warning will show at: {warning_time.strftime('%H:%M:%S')}")

    def quit_app(self, icon=None, item=None):
        """Quit the application"""
        print("Shutting down Workout Snacks...")
        self.save_data()
        self.scheduler.shutdown()
        if self.tray_icon:
            self.tray_icon.stop()

    def run(self):
        """Run the application"""
        print("🏋️  Workout Snacks Started! 🏋️")
        
        # Check if running on Hyprland and provide guidance
        import os
        if os.environ.get('HYPRLAND_INSTANCE_SIGNATURE'):
            print("Detected Hyprland! Make sure you have a system tray widget installed:")
            print("- For Waybar: add 'tray' to modules")
            print("- For other bars: check their tray configuration")
        
        print("Check your system tray for the workout icon.")
        print("Press Ctrl+C to quit.")
        print()

        # Start scheduler
        self.scheduler.start()
        self.schedule_next_workout()

        # Create and run tray icon
        self.tray_icon = self.create_tray_icon()

        try:
            self.tray_icon.run()
        except KeyboardInterrupt:
            self.quit_app()
        except Exception as e:
            print(f"Tray icon error: {e}")
            print("System tray may not be available. Use CLI version instead:")
            print("python workout_cli.py daemon")
            self.quit_app()


def main():
    """Main entry point"""
    app = WorkoutSnacksApp()
    app.run()


if __name__ == "__main__":
    main()
