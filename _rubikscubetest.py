# _rubikscubetest.py

import unittest
import numpy as np
from rubikscube import RubiksCube 

class TestRubiksCube(unittest.TestCase):

    def setUp(self):
        self.cube = RubiksCube()

    def assertCubeStateEqual(self, cube, expected_state):
        """Compare two cube states."""
        self.assertTrue(np.array_equal(cube.state, expected_state), 
                        "Cube state does not match the expected state.")

    def test_initialisation_and_solved_state(self):
        """Test that a new cube is in the solved state."""
        self.assertTrue(self.cube.is_solved(), "A newly initialised cube should be solved.")
        
        self.cube.shuffle(1)
        self.assertFalse(self.cube.is_solved(), "A shuffled cube should not be solved.")

    def test_reset_method(self):
        """Test that reset() returns the cube to the solved state."""
        self.cube.shuffle(10)
        self.assertFalse(self.cube.is_solved())
        self.cube.reset()
        self.assertTrue(self.cube.is_solved(), "Cube should be solved after calling reset().")

    def test_single_move_and_inverse(self):
        """A move followed by its inverse should result in the original state."""
        moves = ["U", "D", "L", "R", "F", "B"]
        for move in moves:
            with self.subTest(move=move):
                initial_state = self.cube.state.copy()
                
                self.cube.move(move)
                self.assertFalse(np.array_equal(self.cube.state, initial_state), f"Move {move} did not change the state.")
                
                self.cube.move(f"{move}'")
                self.assertCubeStateEqual(self.cube, initial_state)

    def test_four_moves_cycle(self):
        """Applying any single clockwise move four times returns to the original state."""
        moves = ["U", "D", "L", "R", "F", "B"]
        for move in moves:
            with self.subTest(move=move):
                initial_state = self.cube.state.copy()
                self.cube.move(f"{move} {move} {move} {move}")
                self.assertCubeStateEqual(self.cube, initial_state)

    def test_double_move(self):
        """Applying a double move twice returns to the original state."""
        moves = ["U2", "D2", "L2", "R2", "F2", "B2"]
        for move in moves:
            with self.subTest(move=move):
                initial_state = self.cube.state.copy()
                self.cube.move(move) # Apply first double move
                self.cube.move(move) # Apply second double move
                self.assertCubeStateEqual(self.cube, initial_state)
    
    def test_known_algorithm(self):
        """Test a known sequence of moves (Sune algorithm) and its inverse."""
        sune = "R U R' U R U2 R'"
        sune_inverse = "R U2 R' U' R U' R'"
        
        initial_state = self.cube.state.copy()
        
        self.cube.move(sune)
        self.assertFalse(np.array_equal(self.cube.state, initial_state), "Sune algorithm did not change state.")
        
        self.cube.move(sune_inverse)
        self.assertCubeStateEqual(self.cube, initial_state)

    def test_F_move_correctness(self):
        """Test the F move against a manually verified resulting state."""
        self.cube.move("F")
        
        # Manually create the expected state after an F move on a solved cube
        expected_cube = RubiksCube()
        expected_cube.state[self.cube.F] = np.rot90(expected_cube.state[self.cube.F], k=-1)
        
        up_row = expected_cube.state[self.cube.U, 2, :].copy() # White
        right_col = expected_cube.state[self.cube.R, :, 0].copy() # Red
        down_row = expected_cube.state[self.cube.D, 0, :].copy() # Yellow
        left_col = expected_cube.state[self.cube.L, :, 2].copy() # Orange
        
        expected_cube.state[self.cube.U, 2, :] = np.flip(left_col)
        expected_cube.state[self.cube.R, :, 0] = up_row
        expected_cube.state[self.cube.D, 0, :] = np.flip(right_col)
        expected_cube.state[self.cube.L, :, 2] = down_row
        
        self.assertCubeStateEqual(self.cube, expected_cube.state)
        
    def test_invalid_move_string(self):
        """Test that the move parser raises a ValueError for invalid input."""
        with self.assertRaises(ValueError):
            self.cube.move("A") # Use a character that is not a valid face or rotation.
        with self.assertRaises(ValueError):
            self.cube.move("U3")
        with self.assertRaises(ValueError):
            self.cube.move("F'2")
            
    def test_whole_cube_rotations(self):
        """Test the x, y, and z whole-cube rotations."""
        rotations = ['x', 'y', 'z']
        for rot in rotations:
            with self.subTest(rotation=rot):
                initial_state = self.cube.state.copy()
                
                # Test inverse
                self.cube.move(rot)
                self.assertFalse(np.array_equal(self.cube.state, initial_state), f"Rotation {rot} did not change the state.")
                self.cube.move(f"{rot}'")
                self.assertCubeStateEqual(self.cube, initial_state)

                # Test cycle of 4
                self.cube.move(f"{rot} {rot} {rot} {rot}")
                self.assertCubeStateEqual(self.cube, initial_state)


if __name__ == '__main__':
    # Run directly from the command line
    unittest.main(verbosity=2)

