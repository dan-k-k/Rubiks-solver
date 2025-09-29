# Real-Time Rubik's Cube Solver

This project allows you to solve a 3x3 Rubik's Cube using a **self-facing** webcam. A Convolutional Neural Network determines a cube's unsolved state in real-time. The scanned state is then fed into the Kociemba algorithm to output a solution. Completed with OpenCV.

![Rubik's Cube Solver Demo](images/Rubik_s-example3.gif)

##### Clone the repository:

```
git clone https://github.com/dan-k-k/Rubiks-solver
cd Rubiks-solver
```

##### Create and activate a virtual environment (recommended):

```
# For Windows
python -m venv venv
.\venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

##### Install the required dependencies:

```
pip install -r requirements.txt
```

##### Launch the application:

```
python main.py
```

When prompted in the terminal, choose the Webcam Scanner option (2). Your webcam feed should appear in a full-screen window.

Once all faces are scanned, the optimal solution will be printed in your terminal.

### Training Your Own Model

If you want to improve the model's accuracy or train it on your specific cube type and lighting conditions, you can collect your own dataset.

#### Step 1: Collect New Sticker Images

Run the script:

```
python datacollector.py
# wait and press (1) to save images to the training ('dataset') folder
```

Capture an image with SPACEBAR.
Press the key corresponding to the sticker's colour (w, y, b, g, r, o), from top left to bottom right.

The script will create a (1) dataset/ or (2) test_dataset/ directory. 
Aim for at least 200-300 images per colour under various lighting conditions.

#### Step 2: Train the Classifier

The `trainclassifier.py` script uses the images you collected in 'dataset' (!) to train a new model.
(The `_evaluate_model.py` script uses the images in 'test_dataset' to test the model's final accuracy.)

Run the script:
```
python trainclassifier.py
```
The script will load the images from the dataset/ folder, train the CNN, and evaluate it using
```
python _evaluate_model.py
```

The best-performing model will be saved as models/best_model.keras, overwriting the old one. 
You can now run `main.py` to use your custom-trained model.
