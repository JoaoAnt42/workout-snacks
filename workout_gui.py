#!/usr/bin/env python3
"""
Workout Snacks GUI - Desktop GUI application with built-in timer
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

try:
    from plyer import notification
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from collections import defaultdict, Counter
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Run: uv pip install plyer matplotlib")
    if "tkinter" in str(e):
        print("Also install tkinter: sudo pacman -S tk (Arch) or sudo apt install python3-tk (Ubuntu)")
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
                Exercise("Planche Push-ups", 9, description="Advanced planche position"),
            ],
            "squats": [
                Exercise("Chair Squats", 1, description="Assisted squats with chair"),
                Exercise("Air Squats", 2, description="Bodyweight squats"),
                Exercise("Sumo Squats", 3, description="Wide stance squats"),
                Exercise("Jump Squats", 4, description="Explosive squat jumps"),
                Exercise("Bulgarian Split Squats", 5, description="Rear foot elevated"),
                Exercise("Cossack Squats", 6, description="Side-to-side squats"),
                Exercise("Single Leg Squats", 7, description="Pistol squats"),
                Exercise("Jump Pistol Squats", 8, description="Explosive pistol squats"),
                Exercise("Shrimp Squats", 9, description="Advanced single leg squat"),
            ],
            "pullups": [
                Exercise("Dead Hangs", 1, description="Hanging from bar"),
                Exercise("Negative Pull-ups", 2, description="Slow descent from top"),
                Exercise("Assisted Pull-ups", 3, description="Band or partner assisted"),
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
                Exercise("Bicycle Crunches", 3, description="Alternating elbow to knee"),
                Exercise("Russian Twists", 4, description="Seated twisting motion"),
                Exercise("Mountain Climbers", 5, description="Running in plank position"),
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
            ]
        }
        
        # Set baseline levels based on user's current ability
        self.exercises["pushups"][7].max_reps_achieved = 15  # Single arm
        self.exercises["squats"][1].max_reps_achieved = 20   # Air squats
        self.exercises["pullups"][3].max_reps_achieved = 10  # Pull-ups


class WorkoutGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🏋️ Workout Snacks")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Data setup
        self.data_dir = Path.home() / ".workout-snacks"
        self.data_dir.mkdir(exist_ok=True)
        self.db_file = self.data_dir / "workout_data.db"
        
        self.exercise_db = ExerciseDatabase()
        self.workout_history: List[WorkoutSession] = []
        self.current_exercises = []
        self.current_exercise_index = 0
        self.current_reps = 0
        
        # Timer variables
        self.timer_running = False
        self.timer_seconds = 60
        self.timer_thread = None
        
        self.init_database()
        self.load_data()
        self.create_widgets()
        
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Create exercises table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                name TEXT NOT NULL,
                difficulty_level INTEGER NOT NULL,
                max_reps_achieved INTEGER DEFAULT 0,
                description TEXT,
                UNIQUE(category, name)
            )
        ''')
        
        # Create workout_sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workout_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                duration_minutes INTEGER DEFAULT 3
            )
        ''')
        
        # Create workout_exercises table (many-to-many)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workout_exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                exercise_name TEXT NOT NULL,
                reps_completed INTEGER NOT NULL,
                FOREIGN KEY (session_id) REFERENCES workout_sessions (id)
            )
        ''')
        
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
                cursor.execute('''
                    INSERT OR IGNORE INTO exercises 
                    (category, name, difficulty_level, max_reps_achieved, description) 
                    VALUES (?, ?, ?, ?, ?)
                ''', (category, exercise.name, exercise.difficulty_level, 
                      exercise.max_reps_achieved, exercise.description))
        
        conn.commit()
        conn.close()
    
    def load_data(self):
        """Load workout history and exercise progress from database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Load exercise progress
        cursor.execute('SELECT category, name, max_reps_achieved FROM exercises')
        for category, name, max_reps in cursor.fetchall():
            if category in self.exercise_db.exercises:
                for exercise in self.exercise_db.exercises[category]:
                    if exercise.name == name:
                        exercise.max_reps_achieved = max_reps
                        break
        
        # Load workout history
        cursor.execute('''
            SELECT ws.timestamp, ws.duration_minutes, we.exercise_name, we.reps_completed
            FROM workout_sessions ws
            JOIN workout_exercises we ON ws.id = we.session_id
            ORDER BY ws.timestamp
        ''')
        
        sessions_data = {}
        for timestamp, duration, exercise_name, reps in cursor.fetchall():
            if timestamp not in sessions_data:
                sessions_data[timestamp] = {
                    'duration': duration,
                    'exercises': []
                }
            sessions_data[timestamp]['exercises'].append((exercise_name, reps))
        
        for timestamp, data in sessions_data.items():
            session = WorkoutSession(
                timestamp=datetime.fromisoformat(timestamp),
                exercises=data['exercises'],
                duration_minutes=data['duration']
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
                cursor.execute('''
                    UPDATE exercises 
                    SET max_reps_achieved = ? 
                    WHERE category = ? AND name = ?
                ''', (exercise.max_reps_achieved, category, exercise.name))
        
        conn.commit()
        conn.close()
    
    def save_workout_session(self, session: WorkoutSession):
        """Save a workout session to database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Insert workout session
        cursor.execute('''
            INSERT INTO workout_sessions (timestamp, duration_minutes) 
            VALUES (?, ?)
        ''', (session.timestamp.isoformat(), session.duration_minutes))
        
        session_id = cursor.lastrowid
        
        # Insert workout exercises
        for exercise_name, reps in session.exercises:
            cursor.execute('''
                INSERT INTO workout_exercises (session_id, exercise_name, reps_completed) 
                VALUES (?, ?, ?)
            ''', (session_id, exercise_name, reps))
        
        conn.commit()
        conn.close()
    
    def get_current_exercises(self) -> List[Exercise]:
        """Get 3 exercises for current workout based on progression"""
        import random
        
        # Get one exercise from 3 different categories
        available_categories = list(self.exercise_db.exercises.keys())
        selected_categories = random.sample(available_categories, min(3, len(available_categories)))
        
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
                elif exercise.max_reps_achieved >= 15:  # Lower threshold for progression
                    # Look for next level
                    next_level_exercises = [e for e in exercises if e.difficulty_level == exercise.difficulty_level + 1]
                    if next_level_exercises:
                        current_exercise = next_level_exercises[0]
                    else:
                        current_exercise = exercise  # Stay at current level
                else:
                    current_exercise = exercise
                    break
            
            workout_exercises.append(current_exercise)
        
        return workout_exercises
    
    def create_widgets(self):
        """Create the GUI widgets"""
        # Main title
        title_frame = tk.Frame(self.root, bg='#f0f0f0')
        title_frame.pack(pady=20)
        
        title_label = tk.Label(title_frame, text="🏋️ Workout Snacks", 
                              font=('Arial', 24, 'bold'), bg='#f0f0f0', 
                              fg='#2c3e50')
        title_label.pack()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Workout tab
        self.workout_frame = tk.Frame(self.notebook, bg='#f0f0f0')
        self.notebook.add(self.workout_frame, text="Workout")
        self.create_workout_tab()
        
        # Progress tab
        self.progress_frame = tk.Frame(self.notebook, bg='#f0f0f0')
        self.notebook.add(self.progress_frame, text="Progress")
        self.create_progress_tab()
        
        # Charts tab
        self.charts_frame = tk.Frame(self.notebook, bg='#f0f0f0')
        self.notebook.add(self.charts_frame, text="Charts")
        self.create_charts_tab()
    
    def create_workout_tab(self):
        """Create the workout tab interface"""
        # Exercise info frame
        self.exercise_info_frame = tk.Frame(self.workout_frame, bg='#ecf0f1', relief='raised', bd=2)
        self.exercise_info_frame.pack(fill='x', padx=20, pady=10)
        
        self.exercise_name_label = tk.Label(self.exercise_info_frame, text="Click 'Start Workout' to begin", 
                                           font=('Arial', 18, 'bold'), bg='#ecf0f1')
        self.exercise_name_label.pack(pady=10)
        
        self.exercise_desc_label = tk.Label(self.exercise_info_frame, text="", 
                                           font=('Arial', 12), bg='#ecf0f1', wraplength=400)
        self.exercise_desc_label.pack(pady=5)
        
        self.personal_best_label = tk.Label(self.exercise_info_frame, text="", 
                                           font=('Arial', 10, 'italic'), bg='#ecf0f1', fg='#7f8c8d')
        self.personal_best_label.pack(pady=5)
        
        # Timer frame
        self.timer_frame = tk.Frame(self.workout_frame, bg='#3498db', relief='raised', bd=3)
        self.timer_frame.pack(fill='x', padx=20, pady=10)
        
        timer_title = tk.Label(self.timer_frame, text="Timer", 
                              font=('Arial', 14, 'bold'), bg='#3498db', fg='white')
        timer_title.pack(pady=5)
        
        self.timer_display = tk.Label(self.timer_frame, text="1:00", 
                                     font=('Arial', 36, 'bold'), bg='#3498db', fg='white')
        self.timer_display.pack(pady=10)
        
        # Timer control buttons
        timer_controls = tk.Frame(self.timer_frame, bg='#3498db')
        timer_controls.pack(pady=10)
        
        self.start_timer_btn = tk.Button(timer_controls, text="Start Timer", 
                                        font=('Arial', 12), bg='#27ae60', fg='white',
                                        command=self.start_timer, width=12)
        self.start_timer_btn.pack(side='left', padx=5)
        
        self.stop_timer_btn = tk.Button(timer_controls, text="Stop Timer", 
                                       font=('Arial', 12), bg='#e74c3c', fg='white',
                                       command=self.stop_timer, width=12, state='disabled')
        self.stop_timer_btn.pack(side='left', padx=5)
        
        self.reset_timer_btn = tk.Button(timer_controls, text="Reset Timer", 
                                        font=('Arial', 12), bg='#f39c12', fg='white',
                                        command=self.reset_timer, width=12)
        self.reset_timer_btn.pack(side='left', padx=5)
        
        # Reps counter frame
        self.reps_frame = tk.Frame(self.workout_frame, bg='#e8f5e8', relief='raised', bd=2)
        self.reps_frame.pack(fill='x', padx=20, pady=10)
        
        reps_title = tk.Label(self.reps_frame, text="Reps Counter", 
                             font=('Arial', 14, 'bold'), bg='#e8f5e8')
        reps_title.pack(pady=5)
        
        self.reps_display = tk.Label(self.reps_frame, text="0", 
                                    font=('Arial', 24, 'bold'), bg='#e8f5e8', fg='#27ae60')
        self.reps_display.pack(pady=5)
        
        reps_controls = tk.Frame(self.reps_frame, bg='#e8f5e8')
        reps_controls.pack(pady=10)
        
        self.reps_minus_btn = tk.Button(reps_controls, text="-", 
                                       font=('Arial', 16, 'bold'), bg='#e74c3c', fg='white',
                                       command=self.decrease_reps, width=3)
        self.reps_minus_btn.pack(side='left', padx=5)
        
        self.reps_plus_btn = tk.Button(reps_controls, text="+", 
                                      font=('Arial', 16, 'bold'), bg='#27ae60', fg='white',
                                      command=self.increase_reps, width=3)
        self.reps_plus_btn.pack(side='left', padx=5)
        
        # Control buttons frame
        self.control_frame = tk.Frame(self.workout_frame, bg='#f0f0f0')
        self.control_frame.pack(fill='x', padx=20, pady=20)
        
        self.start_workout_btn = tk.Button(self.control_frame, text="Start Workout", 
                                          font=('Arial', 14, 'bold'), bg='#3498db', fg='white',
                                          command=self.start_workout, height=2, width=15)
        self.start_workout_btn.pack(side='left', padx=10)
        
        self.next_exercise_btn = tk.Button(self.control_frame, text="Next Exercise", 
                                          font=('Arial', 14, 'bold'), bg='#f39c12', fg='white',
                                          command=self.next_exercise, height=2, width=15, state='disabled')
        self.next_exercise_btn.pack(side='left', padx=10)
        
        self.finish_workout_btn = tk.Button(self.control_frame, text="Finish Workout", 
                                           font=('Arial', 14, 'bold'), bg='#27ae60', fg='white',
                                           command=self.finish_workout, height=2, width=15, state='disabled')
        self.finish_workout_btn.pack(side='left', padx=10)
    
    def create_progress_tab(self):
        """Create the progress tab interface"""
        # Progress display area
        self.progress_text = tk.Text(self.progress_frame, font=('Courier', 10), 
                                    wrap='word', state='disabled')
        
        progress_scrollbar = tk.Scrollbar(self.progress_frame)
        progress_scrollbar.pack(side='right', fill='y')
        
        self.progress_text.pack(fill='both', expand=True, padx=20, pady=20)
        self.progress_text.config(yscrollcommand=progress_scrollbar.set)
        progress_scrollbar.config(command=self.progress_text.yview)
        
        # Refresh button
        refresh_btn = tk.Button(self.progress_frame, text="Refresh Progress", 
                               font=('Arial', 12), bg='#3498db', fg='white',
                               command=self.refresh_progress)
        refresh_btn.pack(pady=10)
        
        # Load initial progress
        self.refresh_progress()
    
    def create_charts_tab(self):
        """Create the charts tab interface"""
        self.charts_label = tk.Label(self.charts_frame, text="Charts will be displayed here", 
                                    font=('Arial', 14), bg='#f0f0f0')
        self.charts_label.pack(expand=True)
        
        show_charts_btn = tk.Button(self.charts_frame, text="Show Charts", 
                                   font=('Arial', 12), bg='#3498db', fg='white',
                                   command=self.show_charts)
        show_charts_btn.pack(pady=20)
    
    def start_workout(self):
        """Start a new workout session"""
        self.current_exercises = self.get_current_exercises()
        self.current_exercise_index = 0
        self.current_reps = 0
        
        if not self.current_exercises:
            messagebox.showerror("Error", "No exercises available!")
            return
        
        # Update UI
        self.update_exercise_display()
        self.reset_timer()
        self.reps_display.config(text="0")
        
        # Enable/disable buttons
        self.start_workout_btn.config(state='disabled')
        self.next_exercise_btn.config(state='normal')
        self.finish_workout_btn.config(state='normal')
        
        messagebox.showinfo("Workout Started", "Workout session started! Complete each exercise for 1 minute.")
    
    def update_exercise_display(self):
        """Update the exercise information display"""
        if not self.current_exercises or self.current_exercise_index >= len(self.current_exercises):
            return
        
        exercise = self.current_exercises[self.current_exercise_index]
        self.exercise_name_label.config(text=f"Exercise {self.current_exercise_index + 1}/3: {exercise.name}")
        self.exercise_desc_label.config(text=exercise.description)
        self.personal_best_label.config(text=f"Personal Best: {exercise.max_reps_achieved} reps")
    
    def next_exercise(self):
        """Move to the next exercise"""
        if not self.current_exercises:
            return
        
        # Save current reps for this exercise
        if self.current_exercise_index < len(self.current_exercises):
            exercise = self.current_exercises[self.current_exercise_index]
            # We'll store reps when finishing the workout
        
        self.current_exercise_index += 1
        self.current_reps = 0
        self.reps_display.config(text="0")
        self.reset_timer()
        
        if self.current_exercise_index < len(self.current_exercises):
            self.update_exercise_display()
            messagebox.showinfo("Next Exercise", f"Moving to exercise {self.current_exercise_index + 1}/3")
        else:
            messagebox.showinfo("Workout Complete", "All exercises completed! Click 'Finish Workout' to save.")
            self.next_exercise_btn.config(state='disabled')
    
    def finish_workout(self):
        """Finish the current workout session"""
        if not self.current_exercises:
            return
        
        # Collect reps for all exercises (simplified - using current reps display)
        completed_exercises = []
        for i, exercise in enumerate(self.current_exercises):
            if i == self.current_exercise_index:
                # Current exercise - use displayed reps
                reps = int(self.reps_display.cget("text"))
            else:
                # Previous exercises - would need to track separately in real implementation
                # For now, use 0 or ask user
                reps = 0
            
            completed_exercises.append((exercise.name, reps))
            
            # Update personal best
            if reps > exercise.max_reps_achieved:
                exercise.max_reps_achieved = reps
        
        # Save workout session
        session = WorkoutSession(
            timestamp=datetime.now(),
            exercises=completed_exercises
        )
        self.workout_history.append(session)
        self.save_workout_session(session)
        self.save_data()
        
        # Reset UI
        self.exercise_name_label.config(text="Workout Completed! 💪")
        self.exercise_desc_label.config(text="Great job! Your progress has been saved.")
        self.personal_best_label.config(text="")
        
        self.start_workout_btn.config(state='normal')
        self.next_exercise_btn.config(state='disabled')
        self.finish_workout_btn.config(state='disabled')
        
        self.stop_timer()
        self.reset_timer()
        
        messagebox.showinfo("Workout Saved", "Workout completed and saved! 💪")
        
        # Refresh progress display
        self.refresh_progress()
    
    def start_timer(self):
        """Start the countdown timer"""
        if not self.timer_running:
            self.timer_running = True
            self.start_timer_btn.config(state='disabled')
            self.stop_timer_btn.config(state='normal')
            
            self.timer_thread = threading.Thread(target=self.run_timer)
            self.timer_thread.daemon = True
            self.timer_thread.start()
    
    def stop_timer(self):
        """Stop the countdown timer"""
        self.timer_running = False
        self.start_timer_btn.config(state='normal')
        self.stop_timer_btn.config(state='disabled')
    
    def reset_timer(self):
        """Reset the timer to 1 minute"""
        self.stop_timer()
        self.timer_seconds = 60
        self.timer_display.config(text="1:00", fg='white', bg='#3498db')
    
    def run_timer(self):
        """Run the countdown timer in a separate thread"""
        while self.timer_running and self.timer_seconds > 0:
            minutes = self.timer_seconds // 60
            seconds = self.timer_seconds % 60
            time_str = f"{minutes}:{seconds:02d}"
            
            # Update display on main thread
            self.root.after(0, lambda: self.timer_display.config(text=time_str))
            
            # Change color when time is running low
            if self.timer_seconds <= 10:
                self.root.after(0, lambda: self.timer_display.config(fg='white', bg='#e74c3c'))
            elif self.timer_seconds <= 30:
                self.root.after(0, lambda: self.timer_display.config(fg='white', bg='#f39c12'))
            
            time.sleep(1)
            self.timer_seconds -= 1
        
        # Timer finished
        if self.timer_seconds <= 0:
            self.root.after(0, lambda: self.timer_display.config(text="0:00", fg='white', bg='#e74c3c'))
            self.root.after(0, self.timer_finished)
        
        self.timer_running = False
    
    def timer_finished(self):
        """Handle timer completion"""
        self.start_timer_btn.config(state='normal')
        self.stop_timer_btn.config(state='disabled')
        
        # Play notification sound and show message
        try:
            notification.notify(
                title="Time's Up!",
                message="1 minute completed! Great job!",
                timeout=5,
                app_name="Workout Snacks"
            )
        except:
            pass
        
        messagebox.showinfo("Time's Up!", "1 minute completed! Great job! 💪")
    
    def increase_reps(self):
        """Increase reps counter"""
        current = int(self.reps_display.cget("text"))
        self.reps_display.config(text=str(current + 1))
    
    def decrease_reps(self):
        """Decrease reps counter"""
        current = int(self.reps_display.cget("text"))
        if current > 0:
            self.reps_display.config(text=str(current - 1))
    
    def refresh_progress(self):
        """Refresh the progress display"""
        self.progress_text.config(state='normal')
        self.progress_text.delete(1.0, tk.END)
        
        # Show current exercise levels
        progress_text = "=" * 60 + "\n"
        progress_text += "📊 WORKOUT PROGRESS 📊\n"
        progress_text += "=" * 60 + "\n\n"
        
        progress_text += "Current Exercise Levels:\n"
        for category, exercises in self.exercise_db.exercises.items():
            progress_text += f"\n{category.upper()}:\n"
            for exercise in exercises:
                status = "✓" if exercise.max_reps_achieved > 0 else "○"
                progress_text += f"  {status} {exercise.name}: {exercise.max_reps_achieved} reps (Level {exercise.difficulty_level})\n"
        
        # Show recent workouts
        progress_text += f"\nRecent Workouts ({len(self.workout_history)} total):\n"
        for session in self.workout_history[-5:]:  # Show last 5
            progress_text += f"  {session.timestamp.strftime('%Y-%m-%d %H:%M')}:\n"
            for exercise_name, reps in session.exercises:
                progress_text += f"    - {exercise_name}: {reps} reps\n"
        
        progress_text += "\n" + "=" * 60
        
        self.progress_text.insert(tk.END, progress_text)
        self.progress_text.config(state='disabled')
    
    def show_charts(self):
        """Show workout charts in a separate window"""
        if not self.workout_history:
            messagebox.showinfo("No Data", "No workout data available for charts.")
            return
        
        # Create charts in a separate matplotlib window
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Workout Analytics', fontsize=16, fontweight='bold')
        
        # Prepare data
        dates = [session.timestamp.date() for session in self.workout_history]
        date_counts = Counter(dates)
        
        # Chart 1: Workouts per day
        sorted_dates = sorted(date_counts.keys())
        workout_counts = [date_counts[date] for date in sorted_dates]
        
        ax1.bar(sorted_dates, workout_counts, color='skyblue', alpha=0.7)
        ax1.set_title('Workouts per Day')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Number of Workouts')
        ax1.tick_params(axis='x', rotation=45)
        
        # Chart 2: Reps per minute trend
        exercise_reps = defaultdict(list)
        exercise_dates = defaultdict(list)
        
        for session in self.workout_history:
            for exercise_name, reps in session.exercises:
                exercise_reps[exercise_name].append(reps)
                exercise_dates[exercise_name].append(session.timestamp.date())
        
        # Plot top 3 exercises by frequency
        top_exercises = sorted(exercise_reps.keys(), key=lambda x: len(exercise_reps[x]), reverse=True)[:3]
        colors = ['red', 'green', 'blue']
        
        for i, exercise in enumerate(top_exercises):
            if i < len(colors):
                ax2.plot(exercise_dates[exercise], exercise_reps[exercise], 
                        marker='o', label=exercise, color=colors[i], alpha=0.7)
        
        ax2.set_title('Reps per Minute Trend (Top 3 Exercises)')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Reps per Minute')
        ax2.legend()
        ax2.tick_params(axis='x', rotation=45)
        
        # Chart 3: Exercise distribution
        all_exercises = [exercise_name for session in self.workout_history for exercise_name, _ in session.exercises]
        exercise_counts = Counter(all_exercises)
        
        top_exercises_pie = dict(Counter(all_exercises).most_common(6))
        if top_exercises_pie:
            ax3.pie(top_exercises_pie.values(), labels=top_exercises_pie.keys(), autopct='%1.1f%%')
        ax3.set_title('Exercise Distribution')
        
        # Chart 4: Personal best progression
        pb_data = {}
        for category, exercises in self.exercise_db.exercises.items():
            for exercise in exercises:
                if exercise.max_reps_achieved > 0:
                    pb_data[f"{exercise.name}"] = exercise.max_reps_achieved
        
        if pb_data:
            sorted_pb = sorted(pb_data.items(), key=lambda x: x[1], reverse=True)[:8]
            names, values = zip(*sorted_pb)
            
            ax4.barh(names, values, color='lightgreen', alpha=0.7)
            ax4.set_title('Personal Bests')
            ax4.set_xlabel('Max Reps Achieved')
        
        plt.tight_layout()
        plt.show()
    
    def run(self):
        """Run the GUI application"""
        self.root.mainloop()


def main():
    """Main entry point"""
    app = WorkoutGUI()
    app.run()


if __name__ == "__main__":
    main()