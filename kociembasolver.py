# kociembasolver.py

import kociemba
from rubikscube import RubiksCube

def solve_with_kociemba(cube_obj):
    
    # Kociemba requires a fixed mapping: U, R, F, D, L, B
    center_pieces = {
        cube_obj.state[cube_obj.U, 1, 1]: 'U',
        cube_obj.state[cube_obj.R, 1, 1]: 'R',
        cube_obj.state[cube_obj.F, 1, 1]: 'F',
        cube_obj.state[cube_obj.D, 1, 1]: 'D',
        cube_obj.state[cube_obj.L, 1, 1]: 'L',
        cube_obj.state[cube_obj.B, 1, 1]: 'B'
    }

    try:
        kociemba_str = ""
        face_order = [cube_obj.U, cube_obj.R, cube_obj.F, cube_obj.D, cube_obj.L, cube_obj.B]
        for face_idx in face_order:
            for row in range(3):
                for col in range(3):
                    color_code = cube_obj.state[face_idx, row, col]
                    kociemba_str += center_pieces[color_code]
    except KeyError:
        return "Error: Could not map cube colors. Ensure cube state is valid."

    try:
        solution = kociemba.solve(kociemba_str)
        return solution
    except Exception as e:
        return f"Error: The cube state is very likely invalid or unsolvable. Kociemba error: {e}"


if __name__ == "__main__":
    # Create a new cube and shuffle it
    scrambled_cube = RubiksCube()
    print("Scrambled Cube State")
    scrambled_cube.shuffle(30)
    print(scrambled_cube)

    # Solve the cube
    print("\nSolving the cube...")
    solution_moves = solve_with_kociemba(scrambled_cube)
    print(f"Solution Found: {solution_moves}")
    
    if "Error" not in solution_moves:
        # Apply the solution to our cube object to verify
        print("\nApplying solution to scrambled cube...")
        scrambled_cube.move(solution_moves)
        print(scrambled_cube)
        print(f"\nIs the cube solved after applying the solution? {scrambled_cube.is_solved()}")

    # --- Test with an invalid cube ---
    print("\n" + "-"*40)
    print("\nTesting with a known unsolvable cube (flipped edge)")
    unsolvable_cube = RubiksCube()
    # Manually flip a single edge piece
    unsolvable_cube.state[unsolvable_cube.U, 0, 1] = unsolvable_cube.state[unsolvable_cube.F, 1, 1]
    unsolvable_cube.state[unsolvable_cube.F, 0, 1] = unsolvable_cube.state[unsolvable_cube.U, 1, 1]
    
    error_solution = solve_with_kociemba(unsolvable_cube)
    print(f"Solver output: {error_solution}")

