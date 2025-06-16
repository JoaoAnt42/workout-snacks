#!/usr/bin/env python3
"""
Workout Snacks GUI - Modern dark-themed desktop GUI application
"""

import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple
from collections import Counter, defaultdict

# Kivy imports
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout

# Chart imports
try:
    from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from plyer import notification


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
            ],
            "stretching_upper": [
                Exercise("Neck Rolls", 1, description="Gentle neck circular movements"),
                Exercise("Shoulder Shrugs", 2, description="Lift shoulders up and down"),
                Exercise("Arm Circles", 3, description="Large arm circular movements"),
                Exercise("Cross-body Arm Stretch", 4, description="Pull arm across chest"),
                Exercise("Overhead Tricep Stretch", 5, description="Reach arm behind head"),
                Exercise("Upper Back Stretch", 6, description="Clasp hands, round back"),
                Exercise("Chest Doorway Stretch", 7, description="Stretch in doorway"),
                Exercise("Eagle Arms", 8, description="Wrap arms around torso"),
                Exercise("Full Shoulder Flow", 9, description="Dynamic shoulder sequence"),
            ],
            "stretching_lower": [
                Exercise("Ankle Circles", 1, description="Rotate ankles in circles"),
                Exercise("Calf Raises", 2, description="Rise up on toes"),
                Exercise("Standing Quad Stretch", 3, description="Hold foot behind you"),
                Exercise("Standing Forward Fold", 4, description="Touch toes while standing"),
                Exercise("Hip Circles", 5, description="Circular hip movements"),
                Exercise("Leg Swings", 6, description="Front to back leg swings"),
                Exercise("Pigeon Pose", 7, description="Hip flexor stretch"),
                Exercise("Figure-4 Stretch", 8, description="Hip and glute stretch"),
                Exercise("Dynamic Leg Flow", 9, description="Full leg stretching sequence"),
            ],
            "stretching_core": [
                Exercise("Torso Twists", 1, description="Side to side torso rotation"),
                Exercise("Side Bends", 2, description="Lean to each side"),
                Exercise("Cat-Cow Stretch", 3, description="Spinal flexibility stretch"),
                Exercise("Seated Spinal Twist", 4, description="Twist spine while seated"),
                Exercise("Cobra Stretch", 5, description="Arch back, open chest"),
                Exercise("Child's Pose", 6, description="Rest pose, stretch back"),
                Exercise("Bridge Pose", 7, description="Lift hips, open hip flexors"),
                Exercise("Full Spinal Roll", 8, description="Roll spine vertebra by vertebra"),
                Exercise("Dynamic Core Flow", 9, description="Full body stretching sequence"),
            ],
        }


class WorkoutGUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 0
        self.padding = 0

        # Dark theme colors
        self.bg_color = (0.12, 0.12, 0.15, 1)  # Dark background
        self.card_color = (0.18, 0.18, 0.22, 1)  # Card background
        self.purple_accent = (0.51, 0.31, 0.87, 1)  # Purple accent
        self.text_primary = (0.95, 0.95, 0.95, 1)  # Light text
        self.text_secondary = (0.7, 0.7, 0.75, 1)  # Secondary text
        
        # Data setup
        self.data_dir = Path.home() / ".workout-snacks"
        self.data_dir.mkdir(exist_ok=True)
        self.db_file = self.data_dir / "workout_data.db"

        self.exercise_db = ExerciseDatabase()
        self.workout_history: List[WorkoutSession] = []
        self.current_exercises = []
        self.current_exercise_index = 0
        self.current_reps = 0
        self.current_view = 'dashboard'
        self.session_reps = []  # Track reps for each exercise in current session

        # Timer variables
        self.timer_running = False
        self.timer_seconds = 60
        self.timer_event = None

        self.init_database()
        self.load_data()
        self.create_widgets()
        self.setup_dark_background()

    def setup_dark_background(self):
        """Setup dark theme background"""
        with self.canvas.before:
            Color(*self.bg_color)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_bg_rect, pos=self.update_bg_rect)
        
    def update_bg_rect(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def create_widgets(self):
        """Create the modern GUI widgets"""
        # Create main container
        self.main_container = BoxLayout(orientation='vertical', spacing=0)
        
        # Create dashboard view
        self.create_dashboard()
        
        self.add_widget(self.main_container)
        
    def create_dashboard(self):
        """Create the main dashboard with charts and navigation"""
        dashboard = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
        
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(80))
        with header.canvas.before:
            Color(*self.card_color)
            header_rect = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=lambda i, v: setattr(header_rect, 'size', i.size), 
                   pos=lambda i, v: setattr(header_rect, 'pos', i.pos))
        
        title = Label(
            text='💪 Workout Snacks',
            font_size=dp(28),
            bold=True,
            color=self.text_primary,
            halign='left',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(title)
        
        # Time since last workout
        self.last_workout_label = Label(
            text=self.get_time_since_last_workout(),
            font_size=dp(14),
            color=self.text_secondary,
            halign='right',
            valign='middle'
        )
        self.last_workout_label.bind(size=self.last_workout_label.setter('text_size'))
        header.add_widget(self.last_workout_label)
        
        dashboard.add_widget(header)
        
        # Stats section
        stats_layout = BoxLayout(orientation='horizontal', spacing=dp(20), size_hint_y=0.6)
        
        # Sessions per day stats
        sessions_container = self.create_chart_container("Recent Activity")
        sessions_stats = self.create_sessions_stats_widget()
        sessions_container.add_widget(sessions_stats)
        stats_layout.add_widget(sessions_container)
        
        # Exercises unlocked stats
        progress_container = self.create_chart_container("Exercise Progress")
        progress_stats = self.create_progress_stats_widget()
        progress_container.add_widget(progress_stats)
        stats_layout.add_widget(progress_container)
        
        dashboard.add_widget(stats_layout)
        
        # Navigation buttons
        nav_layout = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint_y=None, height=dp(80))
        
        start_btn = self.create_nav_button('Start Workout', self.start_workout_view)
        charts_btn = self.create_nav_button('View Charts', self.show_charts_view)
        progress_btn = self.create_nav_button('Progress', self.show_progress_view)
        
        nav_layout.add_widget(start_btn)
        nav_layout.add_widget(charts_btn)
        nav_layout.add_widget(progress_btn)
        
        dashboard.add_widget(nav_layout)
        
        self.main_container.add_widget(dashboard)
        
        # Schedule timer updates
        Clock.schedule_interval(self.update_last_workout_timer, 60.0)  # Update every minute
    
    def create_chart_container(self, title):
        """Create a styled container for charts"""
        container = BoxLayout(orientation='vertical', spacing=dp(10))
        
        # Card background
        with container.canvas.before:
            Color(*self.card_color)
            card_rect = Rectangle(size=container.size, pos=container.pos)
        container.bind(size=lambda i, v: setattr(card_rect, 'size', i.size),
                      pos=lambda i, v: setattr(card_rect, 'pos', i.pos))
        
        # Title
        title_label = Label(
            text=title,
            font_size=dp(16),
            bold=True,
            color=self.text_primary,
            size_hint_y=None,
            height=dp(40)
        )
        container.add_widget(title_label)
        
        return container
    
    def create_nav_button(self, text, callback):
        """Create a styled navigation button"""
        btn = Button(
            text=text,
            font_size=dp(16),
            bold=True,
            background_color=self.purple_accent,
            color=self.text_primary
        )
        btn.bind(on_press=lambda x: callback())
        return btn
    
    def get_time_since_last_workout(self):
        """Get formatted time since last workout"""  
        if not self.workout_history:
            return "No workouts yet"
        
        last_workout = max(session.timestamp for session in self.workout_history)
        time_diff = datetime.now() - last_workout
        
        if time_diff.days > 0:
            return f"Last workout: {time_diff.days} day{'s' if time_diff.days > 1 else ''} ago"
        elif time_diff.seconds > 3600:
            hours = time_diff.seconds // 3600
            return f"Last workout: {hours} hour{'s' if hours > 1 else ''} ago"
        else:
            minutes = time_diff.seconds // 60
            return f"Last workout: {minutes} minute{'s' if minutes > 1 else ''} ago"
    
    def update_last_workout_timer(self, dt):
        """Update the last workout timer"""
        if hasattr(self, 'last_workout_label'):
            self.last_workout_label.text = self.get_time_since_last_workout()
    
    def create_workouts_per_day_chart(self):
        """Create workouts per day bar chart"""
        if not MATPLOTLIB_AVAILABLE:
            return Label(text="Matplotlib not available")
            
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(6, 4), facecolor='#2e2e37')
        ax.set_facecolor('#2e2e37')
        
        # Get last 14 days
        today = datetime.now().date()
        dates = [(today - timedelta(days=i)) for i in range(13, -1, -1)]
        
        # Count workouts per day
        workout_dates = [session.timestamp.date() for session in self.workout_history]
        date_counts = Counter(workout_dates)
        counts = [date_counts.get(date, 0) for date in dates]
        
        # Create bar chart
        bars = ax.bar(range(len(dates)), counts, color=self.purple_accent[:3], alpha=0.8)
        
        # Style the chart
        ax.set_xlabel('Date', color='white', fontsize=10)
        ax.set_ylabel('Workouts', color='white', fontsize=10)
        ax.set_xticks(range(0, len(dates), 2))  # Show every other date
        ax.set_xticklabels([dates[i].strftime('%m/%d') for i in range(0, len(dates), 2)], 
                          rotation=45, color='white', fontsize=8)
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            if count > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                       str(count), ha='center', va='bottom', color='white', fontsize=8)
        
        plt.tight_layout()
        return FigureCanvasKivyAgg(fig)
    
    def create_sessions_stats_widget(self):
        """Create sessions per day statistics widget"""
        stats_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Get last 7 days data
        today = datetime.now().date()
        dates = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
        workout_dates = [session.timestamp.date() for session in self.workout_history]
        date_counts = Counter(workout_dates)
        
        # Sessions per day for last 7 days
        sessions_text = "Last 7 Days:\n"
        total_sessions = 0
        for date in dates:
            count = date_counts.get(date, 0)
            total_sessions += count
            sessions_text += f"{date.strftime('%m/%d')}: {count} sessions\n"
        
        # Calculate average
        avg_sessions = total_sessions / 7
        sessions_text += f"\nAverage: {avg_sessions:.1f} sessions/day"
        
        sessions_label = Label(
            text=sessions_text,
            font_size=dp(12),
            color=self.text_primary,
            halign='left',
            valign='top'
        )
        sessions_label.bind(size=sessions_label.setter('text_size'))
        stats_layout.add_widget(sessions_label)
        
        return stats_layout
    
    def create_progress_stats_widget(self):
        """Create exercises unlocked statistics widget"""
        stats_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Count unlocked exercises
        total_exercises = sum(len(exercises) for exercises in self.exercise_db.exercises.values())
        unlocked_exercises = 0
        
        for exercises in self.exercise_db.exercises.values():
            for exercise in exercises:
                if exercise.max_reps_achieved > 0:
                    unlocked_exercises += 1
        
        # Create progress text
        progress_text = f"Exercises Unlocked:\n\n{unlocked_exercises}/{total_exercises}\n\n"
        progress_percentage = (unlocked_exercises / total_exercises) * 100 if total_exercises > 0 else 0
        progress_text += f"{progress_percentage:.1f}% Complete"
        
        progress_label = Label(
            text=progress_text,
            font_size=dp(16),
            color=self.purple_accent,
            halign='center',
            valign='middle',
            bold=True
        )
        progress_label.bind(size=progress_label.setter('text_size'))
        stats_layout.add_widget(progress_label)
        
        return stats_layout

    # Navigation methods
    def start_workout_view(self):
        """Switch to workout view"""
        self.main_container.clear_widgets()
        self.create_workout_interface()
        
    def show_charts_view(self):
        """Show detailed charts in popup"""
        self.show_charts(None)
        
    def show_progress_view(self):
        """Show progress in popup"""
        self.show_progress_popup()

    def create_workout_interface(self):
        """Create the workout interface"""
        workout_layout = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
        
        # Back button
        back_btn = Button(
            text='← Back to Dashboard',
            font_size=dp(14),
            background_color=self.card_color,
            color=self.text_primary,
            size_hint_y=None,
            height=dp(50)
        )
        back_btn.bind(on_press=lambda x: self.return_to_dashboard())
        workout_layout.add_widget(back_btn)
        
        # Exercise info section with dark theme
        exercise_info_layout = BoxLayout(
            orientation='vertical', 
            spacing=dp(5),
            size_hint_y=None,
            height=dp(120)
        )
        with exercise_info_layout.canvas.before:
            Color(*self.card_color)
            exercise_info_rect = Rectangle(size=exercise_info_layout.size, pos=exercise_info_layout.pos)
        exercise_info_layout.bind(size=lambda i, v: setattr(exercise_info_rect, 'size', i.size),
                                 pos=lambda i, v: setattr(exercise_info_rect, 'pos', i.pos))

        self.exercise_name_label = Label(
            text="Click 'Start Workout' to begin",
            font_size=dp(18),
            bold=True,
            color=self.text_primary
        )
        exercise_info_layout.add_widget(self.exercise_name_label)

        self.exercise_desc_label = Label(
            text="",
            font_size=dp(12),
            color=self.text_secondary,
            text_size=(dp(400), None),
            halign='center'
        )
        exercise_info_layout.add_widget(self.exercise_desc_label)

        self.personal_best_label = Label(
            text="",
            font_size=dp(10),
            italic=True,
            color=self.text_secondary
        )
        exercise_info_layout.add_widget(self.personal_best_label)
        
        workout_layout.add_widget(exercise_info_layout)

        # Timer section with dark theme
        timer_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None,
            height=dp(180)
        )
        with timer_layout.canvas.before:
            Color(*self.purple_accent)
            timer_rect = Rectangle(size=timer_layout.size, pos=timer_layout.pos)
        timer_layout.bind(size=lambda i, v: setattr(timer_rect, 'size', i.size),
                         pos=lambda i, v: setattr(timer_rect, 'pos', i.pos))

        timer_title = Label(
            text="Timer",
            font_size=dp(14),
            bold=True,
            color=self.text_primary,
            size_hint_y=None,
            height=dp(30)
        )
        timer_layout.add_widget(timer_title)

        self.timer_display = Label(
            text="1:00",
            font_size=dp(36),
            bold=True,
            color=self.text_primary,
            size_hint_y=None,
            height=dp(60)
        )
        timer_layout.add_widget(self.timer_display)

        # Timer control buttons
        timer_controls = BoxLayout(
            orientation='horizontal',
            spacing=dp(5),
            size_hint_y=None,
            height=dp(50)
        )

        self.start_timer_btn = Button(
            text="Start Timer",
            font_size=dp(12),
            background_color=(0.15, 0.68, 0.38, 1),  # Green
            color=self.text_primary
        )
        self.start_timer_btn.bind(on_press=self.start_timer)
        timer_controls.add_widget(self.start_timer_btn)

        self.stop_timer_btn = Button(
            text="Stop Timer",
            font_size=dp(12),
            background_color=(0.91, 0.30, 0.24, 1),  # Red
            color=self.text_primary,
            disabled=True
        )
        self.stop_timer_btn.bind(on_press=self.stop_timer)
        timer_controls.add_widget(self.stop_timer_btn)

        self.reset_timer_btn = Button(
            text="Reset Timer",
            font_size=dp(12),
            background_color=(0.95, 0.61, 0.07, 1),  # Orange
            color=self.text_primary
        )
        self.reset_timer_btn.bind(on_press=self.reset_timer)
        timer_controls.add_widget(self.reset_timer_btn)
        
        timer_layout.add_widget(timer_controls)
        workout_layout.add_widget(timer_layout)

        # Reps counter section
        reps_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None,
            height=dp(140)
        )
        with reps_layout.canvas.before:
            Color(*self.card_color)
            reps_rect = Rectangle(size=reps_layout.size, pos=reps_layout.pos)
        reps_layout.bind(size=lambda i, v: setattr(reps_rect, 'size', i.size),
                        pos=lambda i, v: setattr(reps_rect, 'pos', i.pos))

        reps_title = Label(
            text="Reps Counter",
            font_size=dp(14),
            bold=True,
            color=self.text_primary,
            size_hint_y=None,
            height=dp(30)
        )
        reps_layout.add_widget(reps_title)

        self.reps_display = Label(
            text="0",
            font_size=dp(24),
            bold=True,
            color=self.purple_accent,
            size_hint_y=None,
            height=dp(40)
        )
        reps_layout.add_widget(self.reps_display)

        reps_controls = BoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )

        # -10 button
        self.reps_minus10_btn = Button(
            text="-10",
            font_size=dp(12),
            bold=True,
            background_color=(0.91, 0.30, 0.24, 1),  # Red
            color=self.text_primary,
            size_hint_x=None,
            width=dp(60)
        )
        self.reps_minus10_btn.bind(on_press=lambda x: self.change_reps(-10))
        reps_controls.add_widget(self.reps_minus10_btn)
        
        # -1 button
        self.reps_minus1_btn = Button(
            text="-1",
            font_size=dp(12),
            bold=True,
            background_color=(0.91, 0.30, 0.24, 1),  # Red
            color=self.text_primary,
            size_hint_x=None,
            width=dp(50)
        )
        self.reps_minus1_btn.bind(on_press=lambda x: self.change_reps(-1))
        reps_controls.add_widget(self.reps_minus1_btn)
        
        # Add spacer
        reps_controls.add_widget(Widget())
        
        # +1 button
        self.reps_plus1_btn = Button(
            text="+1",
            font_size=dp(12),
            bold=True,
            background_color=(0.15, 0.68, 0.38, 1),  # Green
            color=self.text_primary,
            size_hint_x=None,
            width=dp(50)
        )
        self.reps_plus1_btn.bind(on_press=lambda x: self.change_reps(1))
        reps_controls.add_widget(self.reps_plus1_btn)
        
        # +10 button
        self.reps_plus10_btn = Button(
            text="+10",
            font_size=dp(12),
            bold=True,
            background_color=(0.15, 0.68, 0.38, 1),  # Green
            color=self.text_primary,
            size_hint_x=None,
            width=dp(60)
        )
        self.reps_plus10_btn.bind(on_press=lambda x: self.change_reps(10))
        reps_controls.add_widget(self.reps_plus10_btn)
        
        reps_layout.add_widget(reps_controls)
        workout_layout.add_widget(reps_layout)

        # Control buttons
        control_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(60)
        )

        self.start_workout_btn = Button(
            text="Start Workout",
            font_size=dp(14),
            bold=True,
            background_color=self.purple_accent,
            color=self.text_primary
        )
        self.start_workout_btn.bind(on_press=self.start_workout)
        control_layout.add_widget(self.start_workout_btn)

        self.next_exercise_btn = Button(
            text="Next Exercise",
            font_size=dp(14),
            bold=True,
            background_color=(0.95, 0.61, 0.07, 1),  # Orange
            color=self.text_primary,
            disabled=True
        )
        self.next_exercise_btn.bind(on_press=self.next_exercise)
        control_layout.add_widget(self.next_exercise_btn)

        
        workout_layout.add_widget(control_layout)
        self.main_container.add_widget(workout_layout)
        
    def return_to_dashboard(self):
        """Return to the main dashboard"""
        self.main_container.clear_widgets()
        self.create_dashboard()

    def show_progress_popup(self):
        """Show progress in a popup"""
        progress_text = self.generate_progress_text()
        
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        scroll = ScrollView()
        progress_label = Label(
            text=progress_text,
            font_name='DejaVuSansMono',
            font_size=dp(12),
            color=self.text_primary,
            text_size=(dp(600), None),
            halign='left',
            valign='top',
            size_hint_y=None
        )
        progress_label.bind(texture_size=lambda instance, size: setattr(instance, 'height', size[1]))
        scroll.add_widget(progress_label)
        content.add_widget(scroll)
        
        close_btn = Button(
            text='Close',
            size_hint_y=None,
            height=dp(50),
            background_color=self.purple_accent,
            color=self.text_primary
        )
        content.add_widget(close_btn)
        
        popup = Popup(
            title='Workout Progress',
            content=content,
            size_hint=(0.9, 0.9),
            background_color=self.bg_color
        )
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def generate_progress_text(self):
        """Generate progress display text"""
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
        return progress_text

    # Database methods (keeping original implementation)
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

        # Get 3 exercises from different categories (excluding all stretching categories)
        exercise_categories = [cat for cat in self.exercise_db.exercises.keys() if not cat.startswith('stretching')]
        selected_categories = random.sample(
            exercise_categories, min(3, len(exercise_categories))
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
                        current_exercise = exercise  # Stay at current level (maxed exercises still appear)
                else:
                    current_exercise = exercise
                    break

            workout_exercises.append(current_exercise)

        # Add 2 stretching exercises from different categories
        stretching_categories = ['stretching_upper', 'stretching_lower', 'stretching_core']
        selected_stretch_categories = random.sample(stretching_categories, min(2, len(stretching_categories)))
        
        for stretch_category in selected_stretch_categories:
            stretching_exercises = self.exercise_db.exercises.get(stretch_category, [])
            if stretching_exercises:
                # Select appropriate difficulty level for stretching
                available_stretches = []
                for stretch in stretching_exercises:
                    if stretch.max_reps_achieved > 0 or stretch.difficulty_level <= 4:  # Include easy stretches for beginners
                        available_stretches.append(stretch)
                
                if not available_stretches:
                    available_stretches = stretching_exercises[:4]  # Default to first 4 if none unlocked
                
                selected_stretch = random.choice(available_stretches)
                workout_exercises.append(selected_stretch)

        return workout_exercises

    # Workout control methods
    def start_workout(self, instance):
        """Start a new workout session"""
        self.current_exercises = self.get_current_exercises()
        self.current_exercise_index = 0
        self.current_reps = 0
        self.session_reps = []  # Reset session tracking

        if not self.current_exercises:
            self.show_popup("Error", "No exercises available!")
            return

        # Update UI to show first exercise immediately
        self.update_exercise_display()
        self.reset_timer()
        self.reps_display.text = "0"

        # Enable/disable buttons
        self.start_workout_btn.disabled = True
        self.next_exercise_btn.disabled = False
        
        # Auto-start timer for first exercise
        self.start_timer(None)


    def update_exercise_display(self):
        """Update the exercise information display"""
        if not self.current_exercises or self.current_exercise_index >= len(
            self.current_exercises
        ):
            return

        exercise = self.current_exercises[self.current_exercise_index]
        total_exercises = len(self.current_exercises)
        exercise_type = "Stretch" if self.current_exercise_index >= 3 else "Exercise"
        self.exercise_name_label.text = f"{exercise_type} {self.current_exercise_index + 1}/{total_exercises}: {exercise.name}"
        self.exercise_desc_label.text = exercise.description
        self.personal_best_label.text = f"Personal Best: {exercise.max_reps_achieved} reps"

    def next_exercise(self, instance):
        """Move to the next exercise"""
        if not self.current_exercises:
            return

        # Save current exercise reps before moving to next
        current_reps = int(self.reps_display.text)
        self.session_reps.append(current_reps)
        
        # Update personal best if needed
        if self.current_exercise_index < len(self.current_exercises):
            exercise = self.current_exercises[self.current_exercise_index]
            if current_reps > exercise.max_reps_achieved:
                exercise.max_reps_achieved = current_reps

        self.current_exercise_index += 1
        self.current_reps = 0
        self.reps_display.text = "0"
        self.reset_timer()

        if self.current_exercise_index < len(self.current_exercises):
            self.update_exercise_display()
            # Auto-start timer for next exercise
            self.start_timer(None)
        else:
            # Auto-finish workout when all exercises are done
            self.finish_workout(None)
            return

    def finish_workout(self, instance):
        """Finish the current workout session"""
        if not self.current_exercises:
            return

        # Save the last exercise reps if we're finishing mid-workout
        if self.current_exercise_index < len(self.current_exercises):
            current_reps = int(self.reps_display.text)
            self.session_reps.append(current_reps)
            
            # Update personal best for last exercise
            exercise = self.current_exercises[self.current_exercise_index]
            if current_reps > exercise.max_reps_achieved:
                exercise.max_reps_achieved = current_reps

        # Create completed exercises list for saving
        completed_exercises = []
        for i, exercise in enumerate(self.current_exercises):
            if i < len(self.session_reps):
                reps = self.session_reps[i]
                completed_exercises.append((exercise.name, reps))

        # Save workout session
        if completed_exercises:
            session = WorkoutSession(
                timestamp=datetime.now(), exercises=completed_exercises
            )
            self.workout_history.append(session)
            self.save_workout_session(session)
            self.save_data()
        
        # Show progress comparison modal
        self.show_progress_comparison_modal()

        # Reset UI
        self.exercise_name_label.text = "Workout Completed! 💪"
        self.exercise_desc_label.text = "Great job! Your progress has been saved."
        self.personal_best_label.text = ""

        self.start_workout_btn.disabled = False
        self.next_exercise_btn.disabled = True

        self.stop_timer()
        self.reset_timer()

        # Reset workout state (modal will handle returning to dashboard)
        
    def show_progress_comparison_modal(self):
        """Show progress comparison modal at end of workout"""
        if not self.current_exercises or not self.session_reps:
            self.return_to_dashboard()
            return
            
        comparison_text = "🏆 WORKOUT COMPLETE! 🏆\n" + "=" * 50 + "\n\n"
        comparison_text += "Exercise Progress Comparison:\n\n"
        
        improvements = 0
        for i, exercise in enumerate(self.current_exercises):
            if i < len(self.session_reps):
                session_reps = self.session_reps[i]
                previous_best = exercise.max_reps_achieved - session_reps if session_reps > (exercise.max_reps_achieved - session_reps) else exercise.max_reps_achieved
                
                # Determine if this was an improvement
                if session_reps > previous_best:
                    improvements += 1
                    status = "🔥 NEW PERSONAL BEST!"
                elif session_reps == exercise.max_reps_achieved:
                    status = "✅ Matched Personal Best"
                else:
                    status = "📈 Keep practicing"
                
                comparison_text += f"{exercise.name}:\n"
                comparison_text += f"  Today: {session_reps} reps\n"
                comparison_text += f"  Best: {exercise.max_reps_achieved} reps\n"
                comparison_text += f"  {status}\n\n"
        
        if improvements > 0:
            comparison_text += f"🎉 You improved on {improvements} exercise{'s' if improvements > 1 else ''}!\n"
        else:
            comparison_text += "💪 Great workout! Keep pushing for new personal bests!\n"
        
        comparison_text += "\n" + "=" * 50
        
        # Create popup
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        scroll = ScrollView()
        progress_label = Label(
            text=comparison_text,
            font_name='DejaVuSansMono',
            font_size=dp(12),
            color=self.text_primary,
            text_size=(dp(600), None),
            halign='left',
            valign='top',
            size_hint_y=None
        )
        progress_label.bind(texture_size=lambda instance, size: setattr(instance, 'height', size[1]))
        scroll.add_widget(progress_label)
        content.add_widget(scroll)
        
        close_btn = Button(
            text='Continue',
            size_hint_y=None,
            height=dp(50),
            background_color=self.purple_accent,
            color=self.text_primary
        )
        content.add_widget(close_btn)
        
        popup = Popup(
            title='Workout Results',
            content=content,
            size_hint=(0.9, 0.8),
            background_color=self.bg_color
        )
        close_btn.bind(on_press=lambda x: self.close_progress_modal(popup))
        popup.open()
        
    def close_progress_modal(self, popup):
        """Close progress modal and return to dashboard"""
        popup.dismiss()
        self.return_to_dashboard()

    # Timer methods
    def start_timer(self, instance):
        """Start the countdown timer"""
        if not self.timer_running:
            self.timer_running = True
            self.start_timer_btn.disabled = True
            self.stop_timer_btn.disabled = False
            
            # Use Kivy's Clock.schedule_interval
            self.timer_event = Clock.schedule_interval(self.run_timer_tick, 1.0)

    def stop_timer(self, instance=None):
        """Stop the countdown timer"""
        self.timer_running = False
        self.start_timer_btn.disabled = False
        self.stop_timer_btn.disabled = True
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None

    def reset_timer(self, instance=None):
        """Reset the timer to 1 minute"""
        self.stop_timer()
        self.timer_seconds = 60
        self.timer_display.text = "1:00"
        self.timer_display.color = self.text_primary

    def run_timer_tick(self, dt):
        """Run one timer tick using Kivy's Clock"""
        if not self.timer_running or self.timer_seconds <= 0:
            if self.timer_seconds <= 0:
                self.timer_display.text = "0:00"
                self.timer_display.color = self.text_primary
                self.timer_finished()
            self.timer_running = False
            if self.timer_event:
                self.timer_event.cancel()
                self.timer_event = None
            return False  # Stop the clock
            
        # Update display
        minutes = self.timer_seconds // 60
        seconds = self.timer_seconds % 60
        time_str = f"{minutes}:{seconds:02d}"
        self.timer_display.text = time_str

        # Change color when time is running low
        if self.timer_seconds <= 10:
            self.timer_display.color = (1, 0.3, 0.3, 1)  # Red
        elif self.timer_seconds <= 30:
            self.timer_display.color = (1, 0.8, 0.3, 1)  # Orange
        else:
            self.timer_display.color = self.text_primary  # White

        self.timer_seconds -= 1
        return True  # Continue the clock

    def timer_finished(self):
        """Handle timer completion"""
        self.start_timer_btn.disabled = False
        self.stop_timer_btn.disabled = True

        # Play notification sound and show message
        try:
            notification.notify(
                title="Time's Up!",
                message="1 minute completed! Great job!",
                timeout=5,
                app_name="Workout Snacks",
            )
        except Exception:
            pass


    def change_reps(self, change):
        """Change reps by the specified amount"""
        try:
            current = int(self.reps_display.text)
        except ValueError:
            current = 0
        
        new_value = max(0, min(999, current + change))  # Keep between 0 and 999
        self.reps_display.text = str(new_value)
        if hasattr(self, 'reps_input'):
            self.reps_input.text = "0"


    def show_charts(self, instance):
        """Show workout statistics in a popup"""
        if not self.workout_history:
            self.show_popup("No Data", "No workout data available for charts.")
            return

        # Generate statistics text
        stats_content = self.generate_stats_text()
        
        # Create popup with statistics
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        scroll = ScrollView()
        stats_label = Label(
            text=stats_content,
            font_name='DejaVuSansMono',
            font_size=dp(12),
            color=self.text_primary,
            text_size=(dp(600), None),
            halign='left',
            valign='top',
            size_hint_y=None
        )
        stats_label.bind(texture_size=lambda instance, size: setattr(instance, 'height', size[1]))
        scroll.add_widget(stats_label)
        content.add_widget(scroll)
        
        close_btn = Button(
            text='Close',
            size_hint_y=None,
            height=dp(50),
            background_color=self.purple_accent,
            color=self.text_primary
        )
        content.add_widget(close_btn)
        
        popup = Popup(
            title='Workout Statistics',
            content=content,
            size_hint=(0.9, 0.9),
            background_color=self.bg_color
        )
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
        
    def show_popup(self, title, message):
        """Show a simple popup message"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        message_label = Label(
            text=message,
            text_size=(dp(300), None),
            halign='center',
            valign='middle',
            color=self.text_primary
        )
        content.add_widget(message_label)
        
        ok_btn = Button(
            text='OK',
            size_hint_y=None,
            height=dp(50),
            background_color=self.purple_accent,
            color=self.text_primary
        )
        content.add_widget(ok_btn)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(None, None),
            size=(dp(350), dp(200)),
            background_color=self.bg_color
        )
        ok_btn.bind(on_press=popup.dismiss)
        popup.open()

    def generate_stats_text(self):
        """Generate comprehensive workout statistics as text"""
        if not self.workout_history:
            return "No workout data available."

        stats = "=" * 80 + "\n"
        stats += "📊 WORKOUT STATISTICS 📊\n"
        stats += "=" * 80 + "\n\n"

        # Basic stats
        total_workouts = len(self.workout_history)
        stats += f"Total Workouts: {total_workouts}\n"
        
        if self.workout_history:
            first_workout = min(session.timestamp for session in self.workout_history)
            last_workout = max(session.timestamp for session in self.workout_history)
            stats += f"First Workout: {first_workout.strftime('%Y-%m-%d %H:%M')}\n"
            stats += f"Last Workout: {last_workout.strftime('%Y-%m-%d %H:%M')}\n\n"

        # Workouts per day
        dates = [session.timestamp.date() for session in self.workout_history]
        date_counts = Counter(dates)
        stats += "Workouts per Day:\n"
        for date in sorted(date_counts.keys(), reverse=True)[:10]:
            stats += f"  {date}: {date_counts[date]} workout(s)\n"
        stats += "\n"

        # Exercise frequency
        all_exercises = [
            exercise_name
            for session in self.workout_history
            for exercise_name, _ in session.exercises
        ]
        exercise_counts = Counter(all_exercises)
        stats += "Most Frequent Exercises:\n"
        for exercise, count in exercise_counts.most_common(10):
            stats += f"  {exercise}: {count} times\n"
        stats += "\n"

        # Personal bests
        stats += "Personal Bests:\n"
        pb_data = []
        for exercises in self.exercise_db.exercises.values():
            for exercise in exercises:
                if exercise.max_reps_achieved > 0:
                    pb_data.append((exercise.name, exercise.max_reps_achieved))
        
        pb_data.sort(key=lambda x: x[1], reverse=True)
        for name, reps in pb_data[:15]:
            stats += f"  {name}: {reps} reps\n"
        
        stats += "\n" + "=" * 80
        return stats

    def on_stop(self):
        """Handle application stopping"""
        self.timer_running = False
        if self.timer_event:
            self.timer_event.cancel()


class WorkoutSnacksApp(App):
    def build(self):
        return WorkoutGUI()
    
    def get_application_name(self):
        return "Workout Snacks"


def main():
    """Main entry point"""
    WorkoutSnacksApp().run()


if __name__ == "__main__":
    main()