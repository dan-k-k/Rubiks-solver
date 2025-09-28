# Real-Time Rubik's Cube Solver with OpenCV and CNN

This project allows you to solve a physical 3x3 Rubik's Cube using your webcam. A Convolutional Neural Network (CNN) determines a cube's unsolved state in real-time. The scanned state is then fed into the Kociemba algorithm to output a solution.

### Features
- Webcam Scanning: Uses your webcam to detect the cube's state interactively.
- Review & Edit Mode: After capturing a face, you can review the predictions and manually correct any errors before saving.
- Data Collection & Training Scripts: Includes tools for you to collect your own data and train a custom model.

Clone the repository:

```
git clone https://github.com/dan-k-k/Rubiks-solver
cd Rubiks-solver
```

Create and activate a virtual environment (recommended):

```
# For Windows
python -m venv venv
.\venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

Install the required dependencies:

```
pip install -r requirements.txt
```

Running the Solver

Launch the application:
```
python main.py
```

When prompted in the terminal, choose the Webcam Scanner option (2). Your webcam feed should appear in a full-screen window.

### How to Use the Webcam Scanner
Align a Face: Hold one face of the Rubik's Cube up to the camera so that the nine stickers fit inside the on-screen grid.

Follow Orientation Guides: The application will display text on the screen telling you which color face should be on top for a standard orientation (e.g., "Orientation: GREEN face on TOP" when scanning the WHITE face). This is crucial for the solver to work correctly.

Capture: When the predictions look stable, press the SPACEBAR to freeze the frame.

Review: The application will enter 'Review' mode.

Press ENTER to accept the scanned colors and save the face.

Press e to enter 'Edit' mode if a color was predicted incorrectly. Use the arrow keys to select a sticker and the first letter of a color (w, y, b, g, r, o) to change it. Press ENTER to save your edits.

Press r to discard the capture and retry.

Repeat: Continue this process for all 6 faces. The status of each face is shown on the left.

Get the Solution: Once all faces are scanned, the window will close, and the optimal solution will be printed in your terminal.

### Training Your Own Model
If you want to improve the model's accuracy or train it on your specific cube and lighting conditions, you can collect your own dataset.

Step 1: Collect New Sticker Images

The datacollector.py script uses your webcam to take cropped pictures of individual stickers.

Run the script:

python datacollector.py

Hold a sticker inside the center rectangle on the screen.

Press the key corresponding to the sticker's color to save an image:

w - White

y - Yellow

b - Blue

g - Green

r - Red

o - Orange

The script will create a dataset/ and test_dataset/ directory. Images will be saved into sub-folders named after their color. Aim for at least 200-300 images per color under various lighting conditions for a good result.

Step 2: Train the Classifier

The trainclassifier.py script uses the images you collected to train a new model.

Run the script:

python trainclassifier.py

The script will load the images from the dataset/ folder, train the CNN, and evaluate it using the test_dataset/.

Upon completion, the best-performing model will be saved as models/best_model.keras, overwriting the old one. You can now run main.py to use your custom-trained model.
