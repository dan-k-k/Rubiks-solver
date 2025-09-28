# camerainput.py 

import cv2
import numpy as np
import os
from tensorflow.keras.models import load_model
from rubikscube import RubiksCube
from camera_app import CameraApp # base class

class CubeScannerApp(CameraApp):
    """The application for scanning a Rubik's Cube state with live predictions and freeze-frame review."""
    def __init__(self):
        super().__init__("Rubik's Cube CNN Scanner")
        MODEL_PATH = os.path.join('models', 'best_model.keras')
        print(f"Loading colour classification model from: {MODEL_PATH}")
        self.model = load_model(MODEL_PATH)
        print("Model loaded.")
        self.CLASS_LABELS = ['blue', 'green', 'orange', 'red', 'white', 'yellow']
        self.COLOR_TO_INT = {'white': 0, 'yellow': 1, 'blue': 2, 'green': 3, 'red': 4, 'orange': 5}
        self.INT_TO_FACE = {0: "U (White)", 1: "D (Yellow)", 2: "F (Blue)", 3: "B (Green)", 4: "L (Red)", 5: "R (Orange)"}
        self.scanned_faces = {}

        # State management variables
        self.mode = 'ALIGN'  # ALIGN, REVIEW, EDIT
        self.captured_frame = None
        self.captured_predictions = None
        self.edit_selection_index = 4  # Start with centre sticker highlighted
        
    def _predict_colour(self, roi):
        roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        img = cv2.resize(roi_rgb, (32, 32))
        img_array = np.expand_dims(img, axis=0) / 255.0
        prediction = self.model.predict(img_array, verbose=0)
        return self.CLASS_LABELS[np.argmax(prediction)]
    
    def _save_current_face(self):
        """Helper function to save the face state and reset the app mode."""
        if self.captured_predictions is None:
            return
            
        centre_colour_name = self.captured_predictions[4]
        centre_colour_int = self.COLOR_TO_INT.get(centre_colour_name)

        if centre_colour_int is None:
            print("Cannot save: Centre colour is unknown.")
            return

        if centre_colour_int in self.scanned_faces:
            print(f"Face {self.INT_TO_FACE[centre_colour_int]} already scanned.")
        else:
            face_state = [self.COLOR_TO_INT[c] for c in self.captured_predictions]
            mirrored_matrix = np.array(face_state).reshape(3, 3)
            correct_matrix = np.fliplr(mirrored_matrix)
            self.scanned_faces[centre_colour_int] = correct_matrix
            print(f"Scanned and saved face {self.INT_TO_FACE[centre_colour_int]}. {6 - len(self.scanned_faces)} faces remaining.")
        
        # Reset state to go back to alignment mode
        self.mode = 'ALIGN'
        self.captured_frame = None
        self.captured_predictions = None

    def run(self):
        print("\n   Starting Cube Scanner")
        print("1. Align face to see live predictions.")
        print("2. Press SPACEBAR to capture and review.")
        print("3. Press ENTER to accept, 'e' to edit, or 'r' to retry.")

        # This will hold the un-annotated frame during alignment
        clean_frame_for_capture = None

        while len(self.scanned_faces) < 6:
            # Frame Acquisition and Prediction
            if self.mode == 'ALIGN':
                ret, live_frame = self.cap.read()
                if not ret: break
                # Store the flipped frame before any drawing happens.
                clean_frame_for_capture = cv2.flip(live_frame, 1)
                display_frame = clean_frame_for_capture.copy()
            else: # REVIEW or EDIT mode
                display_frame = self.captured_frame.copy()

            # UI Drawing
            sticker_size, gap = 40, 5
            grid_w = (3 * sticker_size) + (2 * gap)
            grid_start_x = (display_frame.shape[1] - grid_w) // 2
            grid_start_y = (display_frame.shape[0] - grid_w) // 2
            
            # Drawing the predictions
            predictions_to_show = None
            if self.mode == 'ALIGN':
                # Run live predictions on every frame
                live_predictions = []
                for i in range(9):
                    row, col = i // 3, i % 3
                    x1 = grid_start_x + col * (sticker_size + gap)
                    y1 = grid_start_y + row * (sticker_size + gap)
                    roi = display_frame[y1:y1 + sticker_size, x1:x1 + sticker_size]
                    live_predictions.append(self._predict_colour(roi))
                predictions_to_show = live_predictions
            else: # REVIEW or EDIT
                predictions_to_show = self.captured_predictions

            # Draw the grid and predictions on the frame
            for i in range(9):
                row, col = i // 3, i % 3
                x1 = grid_start_x + col * (sticker_size + gap)
                y1 = grid_start_y + row * (sticker_size + gap)
                cv2.rectangle(display_frame, (x1, y1), (x1 + sticker_size, y1 + sticker_size), (255, 255, 255), 2)

                if predictions_to_show:
                    colour_name = predictions_to_show[i]
                    cv2.putText(display_frame, colour_name[:1].upper(), (x1 + 5, y1 + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

                if self.mode == 'EDIT' and i == self.edit_selection_index:
                    cv2.rectangle(display_frame, (x1, y1), (x1 + sticker_size, y1 + sticker_size), (0, 255, 0), 4)

            # Show centre face info and instructions
            if predictions_to_show:
                centre_colour_name = predictions_to_show[4]
                centre_colour_int = self.COLOR_TO_INT.get(centre_colour_name)
                if centre_colour_int is not None:
                    cv2.putText(display_frame, f"Showing: {self.INT_TO_FACE[centre_colour_int]}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Add orientation instructions during live alignment
                if self.mode == 'ALIGN':
                    orientation_text = ""
                    if centre_colour_name == 'white':
                        orientation_text = "Orientation: GREEN face on TOP"
                    elif centre_colour_name == 'yellow':
                        orientation_text = "Orientation: BLUE face on TOP"
                    elif centre_colour_name in ['blue', 'green', 'red', 'orange']:
                        orientation_text = "Orientation: WHITE face on TOP"
                    
                    if orientation_text:
                        text_y_pos = display_frame.shape[0] - 80
                        cv2.putText(display_frame, orientation_text, (20, text_y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)

            # Draw status text based on mode
            if self.mode == 'ALIGN':
                cv2.putText(display_frame, "Press SPACEBAR to capture", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            elif self.mode == 'REVIEW':
                cv2.putText(display_frame, "ENTER: Accept | 'e': Edit | 'r': Retry", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            elif self.mode == 'EDIT':
                cv2.putText(display_frame, "Arrows: Move | Colour key: Change | ENTER: Save", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)

            # Face status display
            y_pos = 120
            for i in range(6):
                status = "OK" if i in self.scanned_faces else "Needed"
                colour = (0, 255, 0) if i in self.scanned_faces else (0, 0, 255)
                cv2.putText(display_frame, f"{self.INT_TO_FACE[i]}: {status}", (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, colour, 2)
                y_pos += 30

            self._display_frame(display_frame)

            # Key Handling
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'): break

            if self.mode == 'ALIGN':
                if key == ord(' '):  # SPACEBAR
                    print("Frame captured. Review predictions.")
                    # Save the frame stored earlier, not the one with text on it.
                    self.captured_frame = clean_frame_for_capture.copy()
                    self.captured_predictions = predictions_to_show[:]  # Copy the list
                    self.mode = 'REVIEW'
            
            elif self.mode == 'REVIEW':
                if key == 13:  # ENTER
                    self._save_current_face()
                elif key == ord('e'):
                    self.mode = 'EDIT'
                    self.edit_selection_index = 4
                elif key == ord('r'):
                    self.mode = 'ALIGN'
                    self.captured_frame = None
                    self.captured_predictions = None

            elif self.mode == 'EDIT':
                if key == 82:  # Up arrow
                    self.edit_selection_index = (self.edit_selection_index - 3) % 9
                elif key == 84:  # Down arrow
                    self.edit_selection_index = (self.edit_selection_index + 3) % 9
                elif key == 81:  # Left arrow
                    self.edit_selection_index = (self.edit_selection_index - 1) % 9
                elif key == 83:  # Right arrow
                    self.edit_selection_index = (self.edit_selection_index + 1) % 9
                elif key == 13:  # ENTER
                    self._save_current_face()
                else:
                    key_char = chr(key & 0xFF)
                    colour_map = {'w': 'white', 'y': 'yellow', 'b': 'blue', 'g': 'green', 'r': 'red', 'o': 'orange'}
                    if key_char in colour_map:
                        self.captured_predictions[self.edit_selection_index] = colour_map[key_char]
                        print(f"Set sticker {self.edit_selection_index+1} to {colour_map[key_char]}")

        # Cleanup and Return
        self.cleanup()
        if len(self.scanned_faces) == 6:
            print("\nAll 6 faces scanned successfully!")
            final_state = np.zeros((6, 3, 3), dtype=int)
            for face_int, face_data in self.scanned_faces.items():
                final_state[face_int] = face_data
            return RubiksCube(state=final_state)
        else:
            print("\nScanning was not completed. Exiting.")
            return None

def get_cube_from_camera():
    """Create an instance of the CubeScannerApp and get the cube state."""
    try:
        scanner = CubeScannerApp()
        cube_object = scanner.run()
        return cube_object
    except RuntimeError as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    # Test the scanner directly
    print("Running cube scanner in test mode...")
    cube = get_cube_from_camera()
    if cube:
        print("\nFinal Cube State from test run:")
        print(cube.state)

