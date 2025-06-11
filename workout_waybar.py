#!/usr/bin/env python3
"""
Workout Snacks - Waybar integration for Hyprland
"""

import json
import sqlite3
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

try:
    from plyer import notification
    from apscheduler.schedulers.background import BackgroundScheduler
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Run: pip install plyer apscheduler")
    exit(1)

from workout_cli import WorkoutApp, Exercise


class WorkoutWaybar(WorkoutApp):
    def __init__(self):
        super().__init__()
        self.status_file = Path.home() / ".workout-snacks" / "waybar_status.json"
        self.next_workout_time = None
        self.warning_shown = False
        
    def update_waybar_status(self, text="💪", tooltip="Workout Snacks", warning=False):
        """Update waybar status"""
        status = {
            "text": text,
            "tooltip": tooltip,
            "class": "warning" if warning else "normal",
            "percentage": 100 if warning else 0
        }
        
        try:
            with open(self.status_file, 'w') as f:
                json.dump(status, f)
        except Exception as e:
            print(f"Failed to update waybar status: {e}")
    
    def get_time_until_workout(self) -> str:
        """Get formatted time until next workout"""
        if not self.next_workout_time:
            return "Unknown"
        
        time_left = self.next_workout_time - datetime.now()
        if time_left.total_seconds() <= 0:
            return "Now!"
        
        hours, remainder = divmod(int(time_left.total_seconds()), 3600)
        minutes, _ = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def update_status_display(self):
        """Update the status display with current info"""
        time_left = self.get_time_until_workout()
        total_workouts = len(self.workout_history)
        
        if time_left == "Now!":
            text = "🔥"
            warning = True
        elif self.warning_shown:
            text = "⚠️"
            warning = True
        else:
            text = "💪"
            warning = False
        
        tooltip = f"Next workout: {time_left} | Total workouts: {total_workouts}"
        self.update_waybar_status(text, tooltip, warning)
    
    def workout_reminder(self):
        """Send workout reminder notification"""
        self.send_notification(
            "🏋️ Workout Time!",
            "Time for your exercise snack! Click waybar icon to start."
        )
        self.update_status_display()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Workout reminder sent!")
    
    def workout_warning(self):
        """Show warning 30 minutes before workout"""
        if not self.warning_shown:
            self.send_notification(
                "⚠️ Workout Coming Up",
                "Exercise break in 30 minutes. Prepare to get moving!"
            )
            self.warning_shown = True
            self.update_status_display()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Workout warning sent!")
    
    def schedule_next_workout(self):
        """Schedule the next workout and warning"""
        # Clear existing jobs
        self.scheduler.remove_all_jobs()
        
        # Schedule next workout in 90 minutes
        workout_time = datetime.now() + timedelta(minutes=90)
        warning_time = workout_time - timedelta(minutes=30)
        
        self.scheduler.add_job(
            self.workout_reminder,
            'date',
            run_date=workout_time,
            id='workout_reminder'
        )
        
        self.scheduler.add_job(
            self.workout_warning,
            'date',
            run_date=warning_time,
            id='workout_warning'
        )
        
        # Add periodic status updates
        self.scheduler.add_job(
            self.update_status_display,
            'interval',
            minutes=1,
            id='status_update'
        )
        
        self.next_workout_time = workout_time
        self.warning_shown = False
        self.update_status_display()
        
        print(f"Next workout scheduled for: {workout_time.strftime('%H:%M:%S')}")
        print(f"Warning will show at: {warning_time.strftime('%H:%M:%S')}")
    
    def handle_click(self, button: str):
        """Handle waybar click events"""
        if button == "1":  # Left click
            self.start_workout_interactive()
        elif button == "2":  # Middle click
            self.show_progress()
        elif button == "3":  # Right click
            self.show_quick_menu()
    
    def start_workout_interactive(self):
        """Start workout with notification feedback"""
        try:
            # Run workout in terminal
            subprocess.run(['kitty', '--', 'python', str(Path(__file__).parent / 'workout_cli.py'), 'workout'])
        except:
            try:
                # Fallback terminals
                subprocess.run(['alacritty', '-e', 'python', str(Path(__file__).parent / 'workout_cli.py'), 'workout'])
            except:
                subprocess.run(['gnome-terminal', '--', 'python', str(Path(__file__).parent / 'workout_cli.py'), 'workout'])
        
        # Reset after workout
        self.warning_shown = False
        self.schedule_next_workout()
    
    def show_quick_menu(self):
        """Show quick action menu via rofi/wofi"""
        menu_items = [
            "Start Workout",
            "View Progress", 
            "View Charts",
            "Quit Daemon"
        ]
        
        try:
            # Try wofi first (Wayland native)
            result = subprocess.run([
                'wofi', '--dmenu', '--prompt', 'Workout Action',
                '--lines', str(len(menu_items))
            ], input='\n'.join(menu_items), text=True, capture_output=True)
            
            if result.returncode != 0:
                # Fallback to rofi
                result = subprocess.run([
                    'rofi', '-dmenu', '-p', 'Workout Action'
                ], input='\n'.join(menu_items), text=True, capture_output=True)
            
            choice = result.stdout.strip()
            
            if choice == "Start Workout":
                self.start_workout_interactive()
            elif choice == "View Progress":
                subprocess.run(['kitty', '--', 'python', str(Path(__file__).parent / 'workout_cli.py'), 'progress'])
            elif choice == "View Charts":
                subprocess.run(['kitty', '--', 'python', str(Path(__file__).parent / 'workout_cli.py'), 'charts'])
            elif choice == "Quit Daemon":
                self.quit_daemon()
                
        except Exception as e:
            print(f"Menu error: {e}")
    
    def quit_daemon(self):
        """Quit the daemon"""
        self.update_waybar_status("", "Workout daemon stopped", False)
        self.save_data()
        self.scheduler.shutdown()
        exit(0)
    
    def start_daemon(self):
        """Start waybar-compatible daemon"""
        print("🏋️  Workout Snacks Waybar Daemon Started! 🏋️")
        print(f"Status file: {self.status_file}")
        print("Add this to your waybar config:")
        print("""
{
    "custom/workout": {
        "format": "{}",
        "return-type": "json",
        "exec": "cat ~/.workout-snacks/waybar_status.json",
        "interval": 5,
        "on-click": "python ~/path/to/workout_waybar.py click 1",
        "on-click-middle": "python ~/path/to/workout_waybar.py click 2", 
        "on-click-right": "python ~/path/to/workout_waybar.py click 3"
    }
}
        """)
        print("\nPress Ctrl+C to stop daemon")
        
        # Initialize status
        self.status_file.parent.mkdir(exist_ok=True)
        self.update_waybar_status()
        
        self.scheduler.start()
        self.schedule_next_workout()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.quit_daemon()


def main():
    import sys
    app = WorkoutWaybar()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "click" and len(sys.argv) > 2:
            app.handle_click(sys.argv[2])
        elif sys.argv[1] == "daemon":
            app.start_daemon()
        elif sys.argv[1] == "status":
            app.update_status_display()
            print(json.dumps(json.load(open(app.status_file))))
        else:
            print("Usage: python workout_waybar.py [daemon|click <button>|status]")
    else:
        app.start_daemon()


if __name__ == "__main__":
    main()