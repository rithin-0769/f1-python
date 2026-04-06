"""F1 Track Viewer

A simple replay visualization for the 2024 Las Vegas GP using FastF1 telemetry
and the Arcade graphical framework.
"""

import arcade
import fastf1
import pandas as pd
import numpy as np
import os

# --- CONSTANTS ---
SCREEN_WIDTH = 1200  # Wider to fit Leaderboard
SCREEN_HEIGHT = 800
SCREEN_TITLE = "F1 Replay - Las Vegas GP (Full Grid)"
BACKGROUND_COLOR = arcade.color.BLACK
TRACK_COLOR = arcade.color.WHITE

# Map Team Names to Arcade Colors
TEAM_COLORS = {
    "Red Bull Racing": arcade.color.BLUE,
    "Ferrari": arcade.color.RED,
    "McLaren": arcade.color.ORANGE_PEEL,
    "Mercedes": arcade.color.SILVER,
    "Aston Martin": arcade.color.GO_GREEN,
    "Alpine": arcade.color.FRENCH_BLUE,
    "Williams": arcade.color.DARK_BLUE,
    "RB": arcade.color.BABY_BLUE, # Visa Cash App RB
    "Haas F1 Team": arcade.color.WHITE,
    "Kick Sauber": arcade.color.NEON_GREEN,
}

class F1ReplayWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(BACKGROUND_COLOR)
        
        self.track_points = [] 
        self.map_scale = 0
        self.offset_x = 0
        self.offset_y = 0
        
        self.driver_data = {}      # Stores telemetry
        self.driver_teams = {}     # Stores team color mapping
        
        self.race_time = 0 
        self.playback_speed = 1
        self.is_paused = False
        
        # Leaderboard cache
        self.current_standings = []

    def setup(self):
        print("1. Setting up cache...")
        if not os.path.exists('cache'):
            os.makedirs('cache')
        fastf1.Cache.enable_cache('cache')

        print("2. Downloading Las Vegas 2024 Data (Full Grid)...")
        # Note: Using 2024 as it is the most recent complete dataset available
        # If 2025 is available in your future timeline, change to 2025
        session = fastf1.get_session(2024, 'Las Vegas Grand Prix', 'R')
        session.load()

        print("3. Processing track geometry...")
        lap = session.laps.pick_fastest()
        telemetry = lap.get_telemetry()
        x_data = np.array(telemetry['X'].values)
        y_data = np.array(telemetry['Y'].values)
        self.calculate_track_points(x_data, y_data)
        
        print("4. Loading ALL drivers...")
        # Get list of all driver abbreviations (e.g. ['VER', 'HAM', ...])
        driver_list = session.drivers
        
        for driver_num in driver_list:
            # Look up the abbreviation (e.g. '33' -> 'VER')
            d_info = session.get_driver(driver_num)
            name = d_info['Abbreviation']
            team = d_info['TeamName']
            
            # Store team color
            self.driver_teams[name] = TEAM_COLORS.get(team, arcade.color.GRAY)
            
            print(f"   Processing {name} ({team})...")
            try:
                laps = session.laps.pick_driver(name)
                # get_telemetry() merges GPS and Distance data
                d_tel = laps.get_telemetry()
                d_tel['TimeSeconds'] = d_tel['Time'].dt.total_seconds()
                
                # OPTIMIZATION: We don't need every millisecond. 
                # Resample to keep memory usage lower if needed, but for now we keep raw.
                self.driver_data[name] = d_tel
            except Exception as e:
                print(f"   Skipping {name}: Data error")

        print("5. Ready to race!")

    def calculate_track_points(self, x_coords, y_coords):
        min_x, max_x = np.min(x_coords), np.max(x_coords)
        min_y, max_y = np.min(y_coords), np.max(y_coords)
        
        track_width = max_x - min_x
        track_height = max_y - min_y

        # Shift track to the LEFT to make room for Leaderboard on the RIGHT
        padding = 50 
        available_w = (SCREEN_WIDTH - 250) - (padding * 2) # Reserve 250px for leaderboard
        available_h = SCREEN_HEIGHT - (padding * 2)

        self.map_scale = min(available_w / track_width, available_h / track_height)
        
        # Center in the available space (Left side of screen)
        centered_x = (available_w - (track_width * self.map_scale)) / 2 + padding
        centered_y = (SCREEN_HEIGHT - (track_height * self.map_scale)) / 2
        
        self.offset_x = centered_x - (min_x * self.map_scale)
        self.offset_y = centered_y - (min_y * self.map_scale)

        scaled_x = (x_coords * self.map_scale) + self.offset_x
        scaled_y = (y_coords * self.map_scale) + self.offset_y
        self.track_points = list(zip(scaled_x, scaled_y))

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.SPACE:
            self.is_paused = not self.is_paused
        elif symbol == arcade.key.RIGHT:
            self.playback_speed += 2 # Jump faster
        elif symbol == arcade.key.LEFT:
            self.playback_speed -= 2
            if self.playback_speed < 1: self.playback_speed = 1
        elif symbol == arcade.key.R:
            self.race_time = 0

    def on_update(self, delta_time):
        if not self.is_paused:
            self.race_time += delta_time * self.playback_speed

    def on_draw(self):
        self.clear()
        
        # 1. Draw Track
        if self.track_points:
            arcade.draw_line_strip(self.track_points, TRACK_COLOR, 2)
            
        current_positions = []
            
        # 2. Draw Drivers
        for driver_code, data in self.driver_data.items():
            # Find closest row
            closest_row = data.iloc[(data['TimeSeconds'] - self.race_time).abs().argsort()[:1]]
            
            if not closest_row.empty:
                # Get Position
                raw_x = closest_row['X'].values[0]
                raw_y = closest_row['Y'].values[0]
                
                # Get Distance (for leaderboard sorting)
                dist = closest_row['Distance'].values[0]
                
                screen_x = (raw_x * self.map_scale) + self.offset_x
                screen_y = (raw_y * self.map_scale) + self.offset_y
                
                color = self.driver_teams.get(driver_code, arcade.color.WHITE)
                
                # Draw Car
                arcade.draw_circle_filled(screen_x, screen_y, 5, color)
                arcade.draw_text(driver_code, screen_x + 8, screen_y + 8, color, 9)
                
                # Add to list for leaderboard
                current_positions.append((driver_code, dist, color))

        # 3. Draw Leaderboard
        # Sort drivers by Distance (Highest distance = First place)
        current_positions.sort(key=lambda x: x[1], reverse=True)
        self.draw_leaderboard(current_positions)

        # 4. Draw UI
        minutes = int(self.race_time // 60)
        seconds = int(self.race_time % 60)
        arcade.draw_text(f"Time: {minutes:02d}:{seconds:02d} ({self.playback_speed}x)", 
                         10, SCREEN_HEIGHT - 30, arcade.color.WHITE, 16)

    def draw_leaderboard(self, positions):
        start_x = SCREEN_WIDTH - 200
        start_y = SCREEN_HEIGHT - 50
        
        arcade.draw_text("LEADERBOARD", start_x, start_y, arcade.color.WHITE, 14, bold=True)
        
        y = start_y - 30
        for i, (driver, dist, color) in enumerate(positions):
            # Format: "1. VER"
            text = f"{i+1}. {driver}"
            arcade.draw_text(text, start_x, y, color, 12)
            y -= 25

if __name__ == "__main__":
    app = F1ReplayWindow()
    app.setup()
    arcade.run()