# main.py

from manualinput import get_cube_from_manual_input
from camerainput import get_cube_from_camera
from kociembasolver import solve_with_kociemba
import sys

def display_solution_with_cube_state(solution_str, cube):
    """Split the solution string and display it move by move."""
    moves = solution_str.split()
    total_moves = len(moves)
    
    if not moves:
        print("The cube is already solved!")
        return

    print("The cube state will be updated after each move.")
    print("Keep BLUE facing you, with WHITE on TOP.")
    print("Press [Enter] to see the next move, or type 'q' to quit.\n")

    for i, move in enumerate(moves):
        cube.move(move)
        print("-" * 40)
        print(f"Move {i+1}/{total_moves}:   {move.ljust(3)}")
        print(cube)
        print("-" * 40)
        
        if i < total_moves - 1:
            user_input = input("Press Enter for the next move...")
            if user_input.lower() == 'q':
                print("\nExiting solution steps.")
                return

    print("\n\nSolved!")


def main():
    """The main function for the text-based Rubik's Cube solver application."""
    scrambled_cube = None
    
    while True:
        choice = input("Choose input method:\n1. Manual Text Input\n2. Webcam Scanner\nEnter choice (1 or 2): ")
        if choice == '1':
            scrambled_cube = get_cube_from_manual_input()
            break
        elif choice == '2':
            print("\nStarting webcam scanner...")
            scrambled_cube = get_cube_from_camera()
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")
            
    if scrambled_cube is None:
        print("\nCould not get cube state. Exiting.")
        return

    try:
        print("\nCube state received. Here is the cube you entered:")
        print(scrambled_cube)

        print("\n" + "="*40)
        print("Attempting to solve the cube...")
        solution = solve_with_kociemba(scrambled_cube)

        print("="*40 + "\n")
        if "Error" in solution:
            print("An Error Occurred")
            print(solution)
            print("\nPlease ensure all 54 stickers were entered correctly and form a valid cube.")
        else:
            print("Solution Found!")
            display_solution_with_cube_state(solution, scrambled_cube)

    except (KeyboardInterrupt, SystemExit):
        # Ctrl+C
        print("\nApplication exited.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        print("The program will now exit.")

if __name__ == "__main__":
    main()

