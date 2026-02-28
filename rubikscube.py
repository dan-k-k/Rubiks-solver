# rubikscube.py

import numpy as np
import random

class RubiksCube:
    """
    - 0 (U): Up face (White)
    - 1 (D): Down face (Yellow)
    - 2 (F): Front face (Blue)
    - 3 (B): Back face (Green)
    - 4 (L): Left face (Red)
    - 5 (R): Right face (Orange)
    """

    # Constants for faces for readability
    U, D, F, B, L, R = 0, 1, 2, 3, 4, 5

    def __init__(self, state=None):
        if state is None:
            self.reset()
        else:
            self.state = np.copy(state)

    def reset(self): # To solved state
        self.state = np.array([[[c] * 3 for _ in range(3)] for c in range(6)], dtype=int)

    def is_solved(self):
        for face_idx in range(6):
            centre_colour = self.state[face_idx, 1, 1]
            if not np.all(self.state[face_idx] == centre_colour):
                return False
        return True

    def _apply_move(self, face, clockwise=True): # Single move
        k = 1 if clockwise else 3 # 'k' value for rot90. And for a clockwise cube turn, we need an anti-clockwise array rotation.
        self.state[face] = np.rot90(self.state[face], k=-k)

        for _ in range(k):
            if face == self.U:
                temp = self.state[self.F][0, :].copy()
                self.state[self.F][0, :] = self.state[self.R][0, :]
                self.state[self.R][0, :] = self.state[self.B][0, :]
                self.state[self.B][0, :] = self.state[self.L][0, :]
                self.state[self.L][0, :] = temp
            elif face == self.D:
                temp = self.state[self.F][2, :].copy()
                self.state[self.F][2, :] = self.state[self.L][2, :]
                self.state[self.L][2, :] = self.state[self.B][2, :]
                self.state[self.B][2, :] = self.state[self.R][2, :]
                self.state[self.R][2, :] = temp
            elif face == self.F:
                temp = self.state[self.U][2, :].copy()
                self.state[self.U][2, :] = np.flip(self.state[self.L][:, 2])
                self.state[self.L][:, 2] = self.state[self.D][0, :]
                self.state[self.D][0, :] = np.flip(self.state[self.R][:, 0])
                self.state[self.R][:, 0] = temp
            elif face == self.B:
                temp = self.state[self.U][0, :].copy()
                self.state[self.U][0, :] = self.state[self.R][:, 2]
                self.state[self.R][:, 2] = np.flip(self.state[self.D][2, :])
                self.state[self.D][2, :] = self.state[self.L][:, 0]
                self.state[self.L][:, 0] = np.flip(temp)
            elif face == self.R:
                temp = self.state[self.U][:, 2].copy()
                self.state[self.U][:, 2] = self.state[self.F][:, 2]
                self.state[self.F][:, 2] = self.state[self.D][:, 2]
                self.state[self.D][:, 2] = np.flip(self.state[self.B][:, 0])
                self.state[self.B][:, 0] = np.flip(temp)
            elif face == self.L:
                temp = self.state[self.U][:, 0].copy()
                self.state[self.U][:, 0] = np.flip(self.state[self.B][:, 2])
                self.state[self.B][:, 2] = np.flip(self.state[self.D][:, 0])
                self.state[self.D][:, 0] = self.state[self.F][:, 0]
                self.state[self.F][:, 0] = temp

    def move(self, move_str): # Apply move from string notation
        for move in move_str.split():
            face_char = move[0].upper()
            face_map = {'U': self.U, 'D': self.D, 'F': self.F, 'B': self.B, 'L': self.L, 'R': self.R}
            
            if face_char in face_map:
                face = face_map[face_char]
                if len(move) > 2: raise ValueError(f"Invalid move format: {move}")
                
                if len(move) > 1:
                    modifier = move[1]
                    if modifier == "'": self._apply_move(face, clockwise=False)
                    elif modifier == '2': self._apply_move(face, clockwise=True); self._apply_move(face, clockwise=True)
                    else: raise ValueError(f"Invalid move modifier: {modifier}")
                else:
                    self._apply_move(face, clockwise=True)
            else: # Handle whole-cube rotations
                rotation_map = {'X': self._rotate_x, 'Y': self._rotate_y, 'Z': self._rotate_z}
                if face_char in rotation_map:
                    rotate_func = rotation_map[face_char]
                    if len(move) > 2: raise ValueError(f"Invalid rotation format: {move}")

                    if len(move) > 1:
                        modifier = move[1]
                        if modifier == "'": rotate_func(clockwise=False)
                        elif modifier == '2': rotate_func(clockwise=True); rotate_func(clockwise=True)
                        else: raise ValueError(f"Invalid rotation modifier: {modifier}")
                    else:
                        rotate_func(clockwise=True)
                else:
                    raise ValueError(f"Invalid move character: {face_char}")


    def _rotate_x(self, clockwise=True): # Entire cube
        k = 1 if clockwise else 3
        for _ in range(k):
            temp = self.state[self.F].copy()
            self.state[self.F] = self.state[self.D]
            self.state[self.D] = np.rot90(self.state[self.B], k=2)
            self.state[self.B] = np.rot90(self.state[self.U], k=2)
            self.state[self.U] = temp
            # Rotate side faces
            self.state[self.R] = np.rot90(self.state[self.R], k=-1)
            self.state[self.L] = np.rot90(self.state[self.L], k=1)

    def _rotate_y(self, clockwise=True): # Entire cube
        k = 1 if clockwise else 3
        for _ in range(k):
            temp = self.state[self.F].copy()
            self.state[self.F] = self.state[self.R]
            self.state[self.R] = self.state[self.B]
            self.state[self.B] = self.state[self.L]
            self.state[self.L] = temp
            # Rotate top/bottom faces
            self.state[self.U] = np.rot90(self.state[self.U], k=-1)
            self.state[self.D] = np.rot90(self.state[self.D], k=1)
            
    def _rotate_z(self, clockwise=True): # Entire cube
        k = 1 if clockwise else 3
        for _ in range(k):
            temp = np.rot90(self.state[self.U], k=1)
            self.state[self.U] = np.rot90(self.state[self.L], k=1)
            self.state[self.L] = np.rot90(self.state[self.D], k=1)
            self.state[self.D] = np.rot90(self.state[self.R], k=1)
            self.state[self.R] = temp
            # Rotate front/back faces
            self.state[self.F] = np.rot90(self.state[self.F], k=-1)
            self.state[self.B] = np.rot90(self.state[self.B], k=1)

    def shuffle(self, num_moves=25):
        moves = ["U", "D", "L", "R", "F", "B"]
        modifiers = ["", "'", "2"]
        for _ in range(num_moves):
            random_move = random.choice(moves) + random.choice(modifiers)
            self.move(random_move)

    def __str__(self):
        # Provide a string representation for printing the cube state
        colour_map = {0: 'W', 1: 'Y', 2: 'B', 3: 'G', 4: 'R', 5: 'O', -1: ' '}
        def face_to_str(face_idx):
            return [" ".join(colour_map[c] for c in row) for row in self.state[face_idx]]

        output = []
        up_face, down_face = face_to_str(self.U), face_to_str(self.D)
        left_face, front_face = face_to_str(self.L), face_to_str(self.F)
        right_face, back_face = face_to_str(self.R), face_to_str(self.B)

        for row in up_face: output.append("      " + row)
        output.append("")
        for i in range(3): output.append(f"{left_face[i]}  {front_face[i]}  {right_face[i]}  {back_face[i]}")
        output.append("")
        for row in down_face: output.append("      " + row)
        return "\n".join(output)

if __name__ == "__main__":
    print("Creating a solved Rubik's Cube")
    my_cube = RubiksCube()
    print(my_cube)
    print(f"Is solved? {my_cube.is_solved()}")

    print("Applying a single move: F")
    my_cube.move("F")
    print(my_cube)
    print(f"Is solved? {my_cube.is_solved()}")

    print("Resetting to solved and shuffling the cube with 25 random moves")
    my_cube.reset()
    my_cube.shuffle(25)
    print(my_cube)
    print(f"Is solved? {my_cube.is_solved()}")

