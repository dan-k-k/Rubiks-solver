# datacollector.py

import cv2
import numpy as np
import os
import uuid
from camera_app import CameraApp # base class

class DataCollectorApp(CameraApp):
    """Collecting sticker image data."""
    def __init__(self, target_directory):
        self.DATA_DIR = target_directory
        self.IMG_SIZE = (32, 32)
        self.COLOUR_MAP = {'w': 'white', 'y': 'yellow', 'b': 'blue', 'g': 'green', 'r': 'red', 'o': 'orange'}
        self.BGR_COLOUR_MAP = {'white': (255, 255, 255), 'yellow': (0, 255, 255), 'blue': (255, 0, 0), 'green': (0, 255, 0), 'red': (0, 0, 255), 'orange': (0, 165, 255)}
        self._setup_directories()
        
        super().__init__("Rubik's Cube data collector")

    def _setup_directories(self):
        print(f"Ensuring directories exist in '{self.DATA_DIR}'...")
        for colour_name in self.COLOUR_MAP.values():
            os.makedirs(os.path.join(self.DATA_DIR, colour_name), exist_ok=True)
        print("Directories are ready.")

    def run(self):
        print("\n   Starting Data Collector")
        print("1. Align a face with the grid and press SPACE to capture; 'q' to quit.")
        print("2. Press the key for the highlighted sticker's colour (w,y,b,g,r,o).")
        print("3. Use BACKSPACE to correct, 's' to skip, 'q' to quit.")
        
        while True:
            ret, frame = self.cap.read()
            if not ret: break

            unflipped_frame = cv2.resize(frame, (self.feed_w, self.feed_h))
            annotated_frame = cv2.flip(unflipped_frame, 1)
            
            sticker_size, gap = 50, 7
            grid_w = (3 * sticker_size) + (2 * gap)
            grid_start_x = (self.feed_w - grid_w) // 2
            grid_start_y = (self.feed_h - grid_w) // 2

            for row in range(3):
                for col in range(3):
                    x1 = grid_start_x + col * (sticker_size + gap)
                    y1 = grid_start_y + row * (sticker_size + gap)
                    cv2.rectangle(annotated_frame, (x1, y1), (x1 + sticker_size, y1 + sticker_size), (255, 255, 255), 2)
            cv2.putText(annotated_frame, "Align face and press SPACE, or 'q' to quit.", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            
            self._display_frame(annotated_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'): break
            if key == ord(' '):
                self._capture_and_label_face(unflipped_frame, sticker_size, gap, grid_start_x, grid_start_y)
        
        self.cleanup()
    
    def _capture_and_label_face(self, captured_frame, sticker_size, gap, grid_start_x, grid_start_y):

        flipped_capture = cv2.flip(captured_frame, 1) # Flip because of self-facing camera
        face_data_to_save = [None] * 9
        i = 0
        while i < 9:
            row, col = i // 3, i % 3
            
            display_copy = flipped_capture.copy()
            
            # Main grid
            for r_draw in range(3):
                for c_draw in range(3):
                    dx1 = grid_start_x + c_draw * (sticker_size + gap)
                    dy1 = grid_start_y + r_draw * (sticker_size + gap)
                    cv2.rectangle(display_copy, (dx1, dy1), (dx1 + sticker_size, dy1 + sticker_size), (255, 255, 255), 2)
            
            # Indicate labelled colours
            corner_size = 15
            for idx, data in enumerate(face_data_to_save):
                if data is not None:
                    mem_row, mem_col = idx // 3, idx % 3
                    mem_x1 = grid_start_x + mem_col * (sticker_size + gap)
                    mem_y1 = grid_start_y + mem_row * (sticker_size + gap)
                    bgr_colour = self.BGR_COLOUR_MAP[data['label']]
                    cv2.rectangle(display_copy, (mem_x1, mem_y1), (mem_x1 + corner_size, mem_y1 + corner_size), bgr_colour, -1)

            # Highlight the current sticker
            x1 = grid_start_x + col * (sticker_size + gap)
            y1 = grid_start_y + row * (sticker_size + gap)
            cv2.rectangle(display_copy, (x1, y1), (x1 + sticker_size, y1 + sticker_size), (0, 255, 0), 3)
            cv2.putText(display_copy, "Enter colour (w,y,b,g,r,o), 's' to skip, BACKSPACE, 'q' to quit.", (20, self.feed_h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            self._display_frame(display_copy)
            
            key = cv2.waitKey(0)
            if key in [8, 127]: # Backspace
                i = max(0, i - 1)
                face_data_to_save[i] = None
                continue
            
            key_char = chr(key & 0xFF)
            if key_char == 'q': return
            if key_char == 's':
                face_data_to_save[i] = None
                i += 1
            elif key_char in self.COLOUR_MAP:

                roi = flipped_capture[y1:y1+sticker_size, x1:x1+sticker_size]
                face_data_to_save[i] = {'roi': roi, 'label': self.COLOUR_MAP[key_char]}
                i += 1

        images_to_save = [d for d in face_data_to_save if d is not None]
        if images_to_save:
            print(f"\nSaving {len(images_to_save)} images to '{self.DATA_DIR}'...")
            for data in images_to_save:
                save_path = os.path.join(self.DATA_DIR, data['label'], f"{data['label']}_{uuid.uuid4()}.png")
                cv2.imwrite(save_path, cv2.resize(data['roi'], self.IMG_SIZE))
            print("Save complete.")

if __name__ == "__main__":
    target_dir = None
    while True:
        choice = input("Save images to:\n1. Training dataset (dataset)\n2. Test dataset (test_dataset)\nEnter choice (1 or 2): ")
        if choice == '1':
            target_dir = 'dataset'
            break
        elif choice == '2':
            target_dir = 'test_dataset'
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")

    app = DataCollectorApp(target_directory=target_dir)
    app.run()

