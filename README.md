# AI-Powered Robotic Arm Sorting System

This project is a complete computer vision and robotics pipeline that detects specific objects (e.g., "oranges") using a webcam and a YOLOv8 AI model, determines their position (Left, Center, Right), and commands an Arduino-controlled robotic arm to pick and place the objects accordingly.

## 📂 Project Structure
```text
robotic_sorting_system/
│
├── main.py                # The primary AI loop (vision + sending commands)
├── vision.py              # Handles YOLOv8 object detection logic
├── serial_comm.py         # Handles reliable USB communication
├── config.py              # Stores parameters (COM port, thresholds)
├── gui_test.py            # A graphical app to test camera & motors manually
├── requirements.txt       # Python dependencies list
│
└── robot_arm/
    └── robot_arm.ino      # The C++ code you must upload to the Arduino
```

## 🛠 Hardware Setup

1. **Webcam**: Used for object detection.
2. **Arduino Uno/Nano**: Handles motor control.
3. **4 Servo Motors**:
    - **Base Servo**: Connected to Arduino Pin `3`
    - **Shoulder Servo**: Connected to Arduino Pin `5`
    - **Elbow Servo**: Connected to Arduino Pin `6`
    - **Gripper Servo**: Connected to Arduino Pin `9`

## 🚀 Step-by-Step Usage Guide

### Step 1: Flash the Arduino
1. Open the Arduino IDE.
2. Open the file `robot_arm/robot_arm.ino`.
3. Plug in your Arduino via USB.
4. Select your Board and Port in the IDE (e.g., `COM3`).
5. Click **Upload**.

### Step 2: Configure the System
1. Open `config.py` in your code editor.
2. Change the `COM_PORT` variable (e.g. `"COM3"`) to match exactly what port your Arduino is plugged into (you can check Device Manager on Windows or look at the Arduino IDE dropdown).

### Step 3: Install Python Packages
Open your terminal/command prompt, navigate to this project folder, and run:
```bash
pip install -r requirements.txt
```
*(This will install OpenCV, Ultralytics YOLO, PySerial, and Pillow).*

### Step 4: Test the Connections (Crucial!)
Before running the fully autonomous AI, you should verify the hardware works.
1. Make sure your webcam is uncovered and plugged in.
2. Make sure your Arduino is plugged in via USB.
3. Run the GUI Tester tool:
   ```bash
   python gui_test.py
   ```
4. **What to look for:**
   - The top screen should show your live webcam feed smoothly.
   - The bottom logs should prominently say "Camera OK" and "Connected to COM3".
   - **Action**: Click the "Pick Center", "Pick Left", and "Pick Right" buttons. Your robotic arm should move smoothly to execute a grab and drop sequence. If this works, your hardware is perfectly communicating.

### Step 5: Run the Fully Autonomous AI 🤖
Once you've confirmed the hardware manually works, close the `gui_test.py` window to free up the camera and serial ports. Now, start the autonomous AI script:
```bash
python main.py
```
1. It will load the YOLOv8 model initially.
2. A window will pop up showing the camera feed separated into 3 vertical zones (Left, Center, Right) defined by vertical lines.
3. Place an **orange** (or any orange-like object) in the camera's view.
4. The AI will immediately draw a targeting box around it, classify its zone mathematically, and automatically fire the perfect command to the robotic arm.
5. Press the `ESC` key on your keyboard to stop the program safely when you are done.
