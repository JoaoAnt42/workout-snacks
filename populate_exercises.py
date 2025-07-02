#!/usr/bin/env python3
"""
Exercise Database Population Script
Populates the workout database with extensive exercise progressions based on available equipment.
"""

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set


@dataclass
class Exercise:
    name: str
    difficulty_level: int
    description: str
    equipment_required: Set[str]
    max_reps_achieved: int = 0


class ExercisePopulator:
    def __init__(self):
        self.data_dir = Path.home() / ".workout-snacks"
        self.data_dir.mkdir(exist_ok=True)
        self.db_file = self.data_dir / "workout_data.db"
        
        self.equipment_exercises = {
            "pushups": [
                Exercise("Wall Push-ups", 1, "Push against wall", set()),
                Exercise("Incline Push-ups", 2, "Hands on elevated surface", set()),
                Exercise("Knee Push-ups", 3, "Push-ups on knees", set()),
                Exercise("Regular Push-ups", 4, "Standard push-ups", set()),
                Exercise("Wide Push-ups", 5, "Hands wider than shoulders", set()),
                Exercise("Diamond Push-ups", 6, "Hands in diamond shape", set()),
                Exercise("Decline Push-ups", 7, "Feet elevated", set()),
                Exercise("Pike Push-ups", 8, "Inverted V position", set()),
                Exercise("Archer Push-ups", 9, "One-sided push-ups", set()),
                Exercise("Single Arm Push-ups", 10, "One arm push-ups", set()),
                Exercise("Handstand Push-ups", 11, "Against wall handstand push-ups", set()),
                Exercise("Freestanding Handstand Push-ups", 12, "Freestanding handstand push-ups", set()),
                Exercise("Planche Push-ups", 13, "Advanced planche position", set()),
                Exercise("Weighted Push-ups", 8, "Push-ups with weight vest/backpack", {"dumbbells"}),
                Exercise("Dumbbell Press", 6, "Lying dumbbell chest press", {"dumbbells"}),
                Exercise("Dumbbell Flyes", 7, "Lying dumbbell flyes", {"dumbbells"}),
                Exercise("Barbell Bench Press", 5, "Barbell bench press", {"barbell"}),
                Exercise("Incline Barbell Press", 8, "Incline barbell press", {"barbell"}),
            ],
            
            "squats": [
                Exercise("Chair Squats", 1, "Assisted squats with chair", set()),
                Exercise("Box Squats", 2, "Squats to seated position", set()),
                Exercise("Air Squats", 3, "Bodyweight squats", set()),
                Exercise("Sumo Squats", 4, "Wide stance squats", set()),
                Exercise("Jump Squats", 5, "Explosive squat jumps", set()),
                Exercise("Bulgarian Split Squats", 6, "Rear foot elevated", set()),
                Exercise("Cossack Squats", 7, "Side-to-side squats", set()),
                Exercise("Single Leg Squats", 8, "Pistol squats progression", set()),
                Exercise("Pistol Squats", 9, "Full pistol squats", set()),
                Exercise("Jump Pistol Squats", 10, "Explosive pistol squats", set()),
                Exercise("Shrimp Squats", 11, "Advanced single leg squat", set()),
                Exercise("Dragon Squats", 12, "Advanced shrimp squat variation", set()),
                Exercise("Goblet Squats", 4, "Squats holding weight", {"dumbbells"}),
                Exercise("Dumbbell Squats", 5, "Squats with dumbbells", {"dumbbells"}),
                Exercise("Dumbbell Lunges", 6, "Walking lunges with dumbbells", {"dumbbells"}),
                Exercise("Barbell Back Squats", 7, "Barbell on back squats", {"barbell"}),
                Exercise("Barbell Front Squats", 8, "Barbell front-loaded squats", {"barbell"}),
                Exercise("Barbell Lunges", 7, "Lunges with barbell", {"barbell"}),
            ],
            
            "pullups": [
                Exercise("Dead Hangs", 1, "Hanging from bar", {"pullup_bar"}),
                Exercise("Scapular Pulls", 2, "Shoulder blade engagement", {"pullup_bar"}),
                Exercise("Negative Pull-ups", 3, "Slow descent from top", {"pullup_bar"}),
                Exercise("Assisted Pull-ups", 4, "Band or partner assisted", {"pullup_bar"}),
                Exercise("Regular Pull-ups", 5, "Standard pull-ups", {"pullup_bar"}),
                Exercise("Wide Grip Pull-ups", 6, "Wide grip variation", {"pullup_bar"}),
                Exercise("Chin-ups", 7, "Underhand grip", {"pullup_bar"}),
                Exercise("L-sit Pull-ups", 8, "Pull-ups with L-sit", {"pullup_bar"}),
                Exercise("Commando Pull-ups", 9, "Side-to-side pull-ups", {"pullup_bar"}),
                Exercise("Archer Pull-ups", 10, "One-sided pull-ups", {"pullup_bar"}),
                Exercise("Weighted Pull-ups", 11, "Add weight", {"pullup_bar", "dumbbells"}),
                Exercise("One Arm Pull-ups", 12, "Single arm pull-ups", {"pullup_bar"}),
                Exercise("Muscle-ups", 13, "Pull-up to dip transition", {"pullup_bar"}),
                Exercise("Dumbbell Rows", 5, "Bent over dumbbell rows", {"dumbbells"}),
                Exercise("Single Arm Dumbbell Rows", 6, "One arm dumbbell rows", {"dumbbells"}),
                Exercise("Barbell Rows", 7, "Bent over barbell rows", {"barbell"}),
                Exercise("Barbell Deadlifts", 8, "Conventional deadlifts", {"barbell"}),
            ],
            
            "core": [
                Exercise("Dead Bug", 1, "Lying core stability exercise", set()),
                Exercise("Crunches", 2, "Basic abdominal crunches", set()),
                Exercise("Plank", 3, "Hold plank position (seconds)", set()),
                Exercise("Side Plank", 4, "Side plank hold", set()),
                Exercise("Bicycle Crunches", 5, "Alternating elbow to knee", set()),
                Exercise("Russian Twists", 6, "Seated twisting motion", set()),
                Exercise("Mountain Climbers", 7, "Running in plank position", set()),
                Exercise("Hollow Body Hold", 8, "Hollow position hold", set()),
                Exercise("V-ups", 9, "Full body sit-ups", set()),
                Exercise("L-sits", 10, "Legs at 90 degrees", set()),
                Exercise("Hanging Knee Raises", 8, "Hanging leg raises", {"pullup_bar"}),
                Exercise("Hanging L-sits", 10, "L-sits from pull-up bar", {"pullup_bar"}),
                Exercise("Dragon Flags", 11, "Advanced core exercise", set()),
                Exercise("Human Flag", 12, "Side plank on pole", {"pullup_bar"}),
                Exercise("Weighted Russian Twists", 7, "Russian twists with weight", {"dumbbells"}),
                Exercise("Weighted Plank", 6, "Plank with weight on back", {"dumbbells"}),
            ],
            
            "dips": [
                Exercise("Assisted Dips", 1, "Band or partner assisted", set()),
                Exercise("Bench Dips", 2, "Feet on ground", set()),
                Exercise("Elevated Bench Dips", 3, "Feet elevated", set()),
                Exercise("Chair Dips", 4, "Using two chairs", set()),
                Exercise("Parallel Bar Dips", 5, "Standard dips", {"pullup_bar"}),
                Exercise("Ring Dips", 6, "On gymnastic rings", {"pullup_bar"}),
                Exercise("Weighted Dips", 7, "Add weight", {"pullup_bar", "dumbbells"}),
                Exercise("Archer Dips", 8, "One-sided dips", {"pullup_bar"}),
                Exercise("Single Bar Dips", 9, "On single bar", {"pullup_bar"}),
                Exercise("Impossible Dips", 10, "Advanced ring dips", {"pullup_bar"}),
            ],
            
            "cardio": [
                Exercise("Marching in Place", 1, "Low impact marching", set()),
                Exercise("Jumping Jacks", 2, "Basic jumping jacks", set()),
                Exercise("High Knees", 3, "Running in place", set()),
                Exercise("Butt Kickers", 4, "Heel to glute kicks", set()),
                Exercise("Burpees", 5, "Full body exercise", set()),
                Exercise("Mountain Climbers", 6, "Fast mountain climbers", set()),
                Exercise("Star Jumps", 7, "Explosive star position", set()),
                Exercise("Tuck Jumps", 8, "Knees to chest jumps", set()),
                Exercise("Squat Jumps", 9, "Continuous squat jumps", set()),
                Exercise("Burpee Box Jumps", 10, "Burpee with box jump", set()),
                Exercise("Devil Press", 11, "Burpee with dumbbells", {"dumbbells"}),
                Exercise("Dumbbell Swings", 6, "Kettlebell swing motion with dumbbell", {"dumbbells"}),
                Exercise("Dumbbell Thrusters", 8, "Squat to overhead press", {"dumbbells"}),
                Exercise("Treadmill Walk", 2, "Brisk walking", {"treadmill"}),
                Exercise("Treadmill Jog", 4, "Light jogging", {"treadmill"}),
                Exercise("Treadmill Run", 6, "Moderate running", {"treadmill"}),
                Exercise("Treadmill Sprint Intervals", 8, "High intensity intervals", {"treadmill"}),
                Exercise("Treadmill Hill Walk", 5, "Incline walking", {"treadmill"}),
                Exercise("Treadmill Hill Run", 9, "Incline running", {"treadmill"}),
            ],
            
            "yoga": [
                Exercise("Child's Pose", 1, "Restorative kneeling pose", set()),
                Exercise("Cat-Cow Stretch", 2, "Spinal mobility exercise", set()),
                Exercise("Downward Dog", 3, "Inverted V stretch", set()),
                Exercise("Sun Salutation A", 4, "Basic sun salutation sequence", set()),
                Exercise("Warrior I", 5, "Standing lunge pose", set()),
                Exercise("Warrior II", 6, "Standing wide-legged pose", set()),
                Exercise("Triangle Pose", 7, "Standing side stretch", set()),
                Exercise("Tree Pose", 8, "Standing balance pose", set()),
                Exercise("Crow Pose", 9, "Arm balance pose", set()),
                Exercise("Headstand", 10, "Inverted balance pose", set()),
                Exercise("Handstand", 11, "Advanced inverted pose", set()),
                Exercise("Scorpion Pose", 12, "Advanced backbend inversion", set()),
            ],
            
            "stretches": [
                Exercise("Neck Rolls", 1, "Gentle neck mobility", set()),
                Exercise("Shoulder Rolls", 2, "Shoulder mobility", set()),
                Exercise("Arm Circles", 3, "Dynamic arm stretches", set()),
                Exercise("Hip Circles", 4, "Hip mobility exercise", set()),
                Exercise("Leg Swings", 5, "Dynamic leg stretches", set()),
                Exercise("Hamstring Stretch", 6, "Seated or standing hamstring stretch", set()),
                Exercise("Quad Stretch", 7, "Standing quadriceps stretch", set()),
                Exercise("Calf Stretch", 8, "Wall or standing calf stretch", set()),
                Exercise("Hip Flexor Stretch", 9, "Lunge position hip flexor stretch", set()),
                Exercise("Pigeon Pose", 10, "Deep hip opener", set()),
                Exercise("Butterfly Stretch", 11, "Seated groin stretch", set()),
                Exercise("Spinal Twist", 12, "Seated or lying spinal rotation", set()),
            ]
        }

    def get_user_equipment(self) -> Set[str]:
        """Interactive equipment selection"""
        print("Welcome to Workout Snacks Exercise Database Setup!")
        print("Please select your available equipment:")
        print()
        
        available_equipment = {
            "pullup_bar": "Pull-up bar (or any hanging bar)",
            "dumbbells": "Dumbbells (adjustable or fixed weight)",
            "barbell": "Barbell with weights",
            "treadmill": "Treadmill or running machine"
        }
        
        selected_equipment = set()
        
        for equipment, description in available_equipment.items():
            while True:
                answer = input(f"Do you have {description}? (y/n): ").lower().strip()
                if answer in ['y', 'yes']:
                    selected_equipment.add(equipment)
                    break
                elif answer in ['n', 'no']:
                    break
                else:
                    print("Please answer 'y' for yes or 'n' for no.")
        
        print(f"\nSelected equipment: {', '.join(selected_equipment) if selected_equipment else 'None (bodyweight only)'}")
        print()
        
        return selected_equipment

    def filter_exercises_by_equipment(self, user_equipment: Set[str]) -> Dict[str, List[Exercise]]:
        """Filter exercises based on available equipment"""
        filtered_exercises = {}
        
        for category, exercises in self.equipment_exercises.items():
            filtered_exercises[category] = []
            
            for exercise in exercises:
                if not exercise.equipment_required or exercise.equipment_required.issubset(user_equipment):
                    filtered_exercises[category].append(exercise)
        
        return filtered_exercises

    def init_database(self):
        """Initialize SQLite database with updated schema"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        # Drop existing exercises table to recreate with new schema
        cursor.execute("DROP TABLE IF EXISTS exercises")

        # Create exercises table with equipment field
        cursor.execute("""
            CREATE TABLE exercises (
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

        # Create workout_exercises table
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

    def populate_exercises(self, filtered_exercises: Dict[str, List[Exercise]]):
        """Populate database with filtered exercises"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        total_exercises = 0
        
        for category, exercises in filtered_exercises.items():
            print(f"Adding {len(exercises)} exercises to {category.upper()} category...")
            
            for exercise in exercises:
                equipment_str = ','.join(sorted(exercise.equipment_required)) if exercise.equipment_required else ''
                
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO exercises 
                    (category, name, difficulty_level, max_reps_achieved, description, equipment_required) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        category,
                        exercise.name,
                        exercise.difficulty_level,
                        exercise.max_reps_achieved,
                        exercise.description,
                        equipment_str
                    ),
                )
                total_exercises += 1

        conn.commit()
        conn.close()
        
        print(f"\n✅ Successfully added {total_exercises} exercises to the database!")
        
        # Show summary
        print("\nExercise Summary by Category:")
        for category, exercises in filtered_exercises.items():
            print(f"  {category.upper()}: {len(exercises)} exercises (Levels 1-{max(e.difficulty_level for e in exercises)})")

    def run(self):
        """Main execution flow"""
        print("This will reset your exercise database with new progressions.")
        confirm = input("Continue? (y/n): ").lower().strip()
        
        if confirm not in ['y', 'yes']:
            print("Setup cancelled.")
            return
        
        # Get user equipment
        user_equipment = self.get_user_equipment()
        
        # Filter exercises
        filtered_exercises = self.filter_exercises_by_equipment(user_equipment)
        
        # Initialize database
        print("Initializing database...")
        self.init_database()
        
        # Populate exercises
        self.populate_exercises(filtered_exercises)
        
        print("\n🎉 Exercise database setup complete!")
        print("You can now run 'python workout_cli.py workout' to start your personalized workouts.")


def main():
    populator = ExercisePopulator()
    populator.run()


if __name__ == "__main__":
    main()