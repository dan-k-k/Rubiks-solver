# manualinput.py

import os
import sys
import numpy as np
import readchar
from rubikscube import RubiksCube

# Constants for Readability and Configuration
COLOR_MAP = {'w': 0, 'y': 1, 'b': 2, 'g': 3, 'o': 5, 'r': 4} # Note: Orange=5(Right of blue), Red=4(Left of blue)
DISPLAY_MAP = {v: k.upper() for k, v in COLOR_MAP.items()}
KEY_TO_FACE_MAP = {
    'w': RubiksCube.U, 'y': RubiksCube.D, 'b': RubiksCube.F,
    'g': RubiksCube.B, 'o': RubiksCube.R, 'r': RubiksCube.L # Note: O->R, R->L
}

# Define the order and instructions for face input, matching the user's cube
FACE_ORDER = [
    (RubiksCube.U, "White (Up)", "You are in the 'home' position. The WHITE face is on top."),
    (RubiksCube.D, "Yellow (Down)", "From home, tilt the cube FORWARD TWICE so YELLOW is on top."),
    (RubiksCube.F, "Blue (Front)", "Return to home. The BLUE face is already facing you."),
    (RubiksCube.B, "Green (Back)", "Return to home, then turn the cube AROUND so GREEN is facing you, keeping WHITE on top."),
    (RubiksCube.L, "Red (Left)", "From home, bring the LEFT (Red) face to the front."),
    (RubiksCube.R, "Orange (Right)", "From home, bring the RIGHT (Orange) face to the front.")
]
# Create a reverse map from face_int to details for easier lookup
FACE_DETAILS_MAP = {f[0]: f for f in FACE_ORDER}


VALID_COLOR_KEYS = set(COLOR_MAP.keys())
BACKSPACE_KEYS = {'\x08', '\x7f'}

def _clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def _display_face_grid(face_name, instruction, entered_colors):
    """Displays the current state of the face being entered with instructions."""
    _clear_screen()
    print("--- Rubik's Cube Guided Input ---")
    print("\nIMPORTANT: Always return to the 'home' position before each new face.")
    print("Home Position: WHITE center on top, BLUE center facing you.")
    print("-" * 60)
    print(f"Instruction: {instruction}")
    print(f"\nEnter the 9 colors for the {face_name} face from top-left to bottom-right.")
    print("Press [Backspace] to undo.\n")

    grid = [DISPLAY_MAP.get(c, '.') for c in entered_colors]
    grid += ['.'] * (9 - len(grid))

    print(f"    {grid[0]} {grid[1]} {grid[2]}")
    print(f"    {grid[3]} {grid[4]} {grid[5]}")
    print(f"    {grid[6]} {grid[7]} {grid[8]}")
    print("\nPress Ctrl+C to exit.")

def _display_full_cube_for_confirmation(face_colors_map):
    """Displays the full, unfolded cube state for user confirmation with labels."""
    def get_face_str(face_int):
        colors = face_colors_map.get(face_int, [])
        grid = [DISPLAY_MAP.get(c, '.') for c in colors]
        grid += ['.'] * (9 - len(grid))
        return [f"{grid[0]} {grid[1]} {grid[2]}", f"{grid[3]} {grid[4]} {grid[5]}", f"{grid[6]} {grid[7]} {grid[8]}"]

    up_face = get_face_str(RubiksCube.U)
    down_face = get_face_str(RubiksCube.D)
    left_face = get_face_str(RubiksCube.L)
    front_face = get_face_str(RubiksCube.F)
    right_face = get_face_str(RubiksCube.R)
    back_face = get_face_str(RubiksCube.B)

    _clear_screen()
    print("--- Review Your Cube ---")
    print("This shows the cube 'unfolded'. Home is White on top, Blue in front.\n")

    # Up Face (White)
    for row in up_face: print("       " + row)
    print("")

    # Middle Band of Faces
    for i in range(3):
        print(f"{left_face[i]}  {front_face[i]}  {right_face[i]}  {back_face[i]}")
    print("")

    # Down Face (Yellow)
    for row in down_face: print("       " + row)

def _wait_for_any_key():
    """Waits for the user to press any key."""
    try:
        key = readchar.readkey()
        if key == readchar.key.CTRL_C:
            print("\nExiting.")
            sys.exit(0)
    except KeyboardInterrupt:
        print("\nExiting.")
        sys.exit(0)

def _validate_centers(face_colors_map):
    """Checks if the entered center pieces are valid."""
    if len(face_colors_map) != 6:
        return "Input Error: Not all 6 faces were entered."

    centers = [colors[4] for face, colors in sorted(face_colors_map.items())]
    
    if set(centers) != set(COLOR_MAP.values()):
        center_counts = {c: centers.count(c) for c in centers}
        error_messages = []
        expected_colors = {val: key.upper() for key, val in COLOR_MAP.items()}
        
        for color_val, count in center_counts.items():
            if count > 1:
                error_messages.append(f"{count} '{expected_colors[color_val]}' centers")
        
        missing_colors = set(COLOR_MAP.values()) - set(centers)
        for color_val in missing_colors:
            error_messages.append(f"no '{expected_colors[color_val]}' center")
            
        return f"Input Error: Invalid centers ({', '.join(error_messages)}). Please edit the faces."
    return None # Validation passed

def get_cube_from_manual_input():
    """Guides the user through entering the cube's state via single keypresses."""
    _clear_screen()
    print("--- Welcome to the Rubik's Cube Solver ---")
    print("\nPlease hold your physical cube so that:")
    print("  - The WHITE center is on the TOP face.")
    print("  - The BLUE center is on the FRONT face (facing you).")
    print("\nThis is your 'home' orientation. Press any key to begin...")
    _wait_for_any_key()
    
    face_colors = {}
    faces_to_enter = [f[0] for f in FACE_ORDER]

    while True: # Main loop for confirmation and editing
        
        current_face_list_idx = 0
        while current_face_list_idx < len(faces_to_enter):
            face_int = faces_to_enter[current_face_list_idx]
            _, face_name, instruction = FACE_DETAILS_MAP[face_int]

            current_entries = face_colors.get(face_int, [])
            
            input_complete_for_face = False
            while not input_complete_for_face:
                _display_face_grid(face_name, instruction, current_entries)
                try:
                    key = readchar.readkey()
                    if key == readchar.key.CTRL_C: sys.exit("\nExiting.")
                except KeyboardInterrupt: sys.exit("\nExiting.")

                if key in VALID_COLOR_KEYS:
                    if len(current_entries) < 9:
                        current_entries.append(COLOR_MAP[key])
                elif key in BACKSPACE_KEYS:
                    if current_entries:
                        current_entries.pop()
                    else:
                        if current_face_list_idx > 0:
                            current_face_list_idx -= 1
                            break
                
                if len(current_entries) == 9:
                    input_complete_for_face = True

            face_colors[face_int] = current_entries
            
            if input_complete_for_face:
                current_face_list_idx += 1
        
        # Confirmation step
        _display_full_cube_for_confirmation(face_colors)
        print("\nIs this correct? (y)es / (e)dit a face")
        
        while True:
            action = readchar.readkey().lower()
            if action == 'y':
                validation_error = _validate_centers(face_colors)
                if validation_error:
                    print(f"\n{validation_error}")
                    print("You will be returned to the edit screen. Press any key.")
                    _wait_for_any_key()
                    _display_full_cube_for_confirmation(face_colors)
                    print("\nIs this correct? (y)es / (e)dit a face")
                    continue

                final_state = np.zeros((6, 3, 3), dtype=int)
                for face_int, colors in face_colors.items():
                    final_state[face_int] = np.array(colors).reshape(3, 3)
                print("\n--- All 6 faces have been entered. ---")
                return RubiksCube(state=final_state)
            
            elif action == 'e':
                print("\nWhich face to edit? (w/y/b/g/o/r)")
                face_key = readchar.readkey().lower()
                if face_key in KEY_TO_FACE_MAP:
                    faces_to_enter = [KEY_TO_FACE_MAP[face_key]]
                    break 
                else:
                    print("Invalid face key. Press any key to try again.")
                    _wait_for_any_key()
                    _display_full_cube_for_confirmation(face_colors)
                    print("\nIs this correct? (y)es / (e)dit a face")
            else:
                print("Invalid input. Please press 'y' or 'e'.")

if __name__ == "__main__":
    try:
        user_cube = get_cube_from_manual_input()
        print("\nCube state successfully created!")
        print(user_cube)
    except Exception as e:
        print(f"\nAn error occurred: {e}")

