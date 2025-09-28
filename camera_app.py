# camera_app.py

import cv2
import numpy as np
import sys
from screeninfo import get_monitors

def select_camera():
    """Cycle through available camera indices and let the user select one."""
    print("Searching for cameras...")
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if not cap.isOpened():
            continue

        print(f"Testing camera index {i}...")
        for _ in range(300): # Preview for ~10 seconds
            ret, frame = cap.read()
            if not ret: break
            
            frame = cv2.flip(frame, 1)
            text = f"Camera Index: {i}. Use this camera? (y/n)"
            cv2.putText(frame, text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3, cv2.LINE_AA)
            cv2.putText(frame, text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)
            cv2.imshow('Camera Selection', frame)
            
            key = cv2.waitKey(30) & 0xFF
            if key == ord('y'):
                print(f"Selected camera at index {i}.")
                cv2.destroyWindow('Camera Selection')
                return cap, i
            elif key == ord('n'):
                break
        
        cap.release()
        cv2.destroyWindow('Camera Selection')

    print("No camera was selected.")
    return None, -1

class CameraApp:
    """Handle boilerplate for camera selection, window creation, and display."""
    def __init__(self, window_name):
        self.window_name = window_name
        
        try:
            monitor = get_monitors()[0]
            self.screen_w, self.screen_h = monitor.width, monitor.height
        except Exception:
            self.screen_w, self.screen_h = 1920, 1080

        self.cap, self.camera_index = select_camera()
        if self.cap is None:
            raise RuntimeError("Camera selection failed. Exiting.")

        self.feed_w, self.feed_h = 1280, 720
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.feed_w)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.feed_h)

        cv2.namedWindow(self.window_name, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    def _display_frame(self, frame):
        """Create a canvas and centre the camera feed on it."""
        canvas = np.full((self.screen_h, self.screen_w, 3), 255, dtype=np.uint8)
        h, w, _ = frame.shape
        start_x = (self.screen_w - w) // 2
        start_y = (self.screen_h - h) // 2
        canvas[start_y:start_y + h, start_x:start_x + w] = frame
        cv2.imshow(self.window_name, canvas)

    def cleanup(self):
        """Release the camera and destroy all windows."""
        print("Cleaning up and closing application.")
        self.cap.release()
        cv2.destroyAllWindows()

