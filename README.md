# 🦾 AI-Powered Robotic Arm Sorting System

A complete computer-vision + robotics pipeline that detects objects (e.g. **oranges**) using an external USB webcam and a YOLOv8 AI model, classifies their position (Left / Center / Right), and commands an Arduino-controlled 4-servo robotic arm to pick and place them automatically.

---

## 📁 Project Structure

```text
robotic_sorting_system/
│
├── main.py              ← Primary AI loop (vision + serial commands)
├── vision.py            ← YOLOv8 object detection + debug overlay
├── serial_comm.py       ← Serial communication to Arduino
├── config.py            ← All tunable settings (COM port, camera, thresholds)
├── gui_test.py          ← Manual GUI tester for camera & arm motors
├── scan_cameras.py      ← Utility to detect available camera indices
├── diagnose_camera.py   ← In-depth diagnostic tool for camera resolution testing
├── requirements.txt     ← Python dependencies
│
└── robot_arm/
    └── robot_arm.ino    ← Arduino firmware (flash this to the Arduino)
```

---

## 🔌 Hardware Connections

### Arduino → Servo Motors

| Servo        | Arduino Pin | Function                     |
|--------------|-------------|------------------------------|
| Base         | **Pin 3**   | Rotates arm Left / Center / Right |
| Shoulder     | **Pin 5**   | Raises/lowers the upper arm  |
| Elbow        | **Pin 6**   | Extends/retracts the forearm |
| Gripper      | **Pin 9**   | Opens and closes the claw    |

> **Power note**: Servo motors draw significant current. Power them from an external 5V supply (e.g. a 2A adapter) with a **shared GND** between the power supply and Arduino. Do NOT power servos directly from the Arduino's 5V pin.

### Servo Wiring (each servo)

| Servo Wire Color | Connect To              |
|------------------|-------------------------|
| Brown / Black    | GND (shared ground)     |
| Red              | 5V external power supply|
| Orange / Yellow  | Arduino Signal Pin (3 / 5 / 6 / 9) |

### Arduino → PC

Connect the Arduino to your laptop via a **USB-A to USB-B cable** (standard Arduino cable).

### External Webcam → PC

| Camera                | Connection |
|-----------------------|------------|
| USB2.0 PC CAMERA      | USB port on laptop |

> The external webcam is firmly assigned to index `1` (720p) and your built-in laptop camera is index `0` (480p). Both `gui_test.py` and `main.py` respect the `CAMERA_INDEX` inside `config.py`. If you experience hardware connection issues, run `python diagnose_camera.py` for a full breakdown.

---

## ⚙️ Arduino: What to Flash

The file to flash is:
```
robotic_sorting_system/robot_arm/robot_arm.ino
```

### What the firmware does
- Listens on **Serial (9600 baud)** for single-letter commands
- `L` → picks from the **Left** zone
- `C` → picks from the **Center** zone
- `R` → picks from the **Right** zone
- After every pick, automatically calls `drop_object()` then `goHome()`
- All servo movements are smooth (`moveSlowly()` — 15ms per degree step)

### Servo positions (tunable in `.ino`)

| Position     | Base | Shoulder | Elbow |
|--------------|------|----------|-------|
| Home         | 90°  | 90°      | 90°   |
| Pick Left    | 135° | 45°      | 45°   |
| Pick Center  | 90°  | 45°      | 45°   |
| Pick Right   | 45°  | 45°      | 45°   |
| Drop         | 0°   | 120°     | 120°  |

### Step-by-Step Arduino Flash Instructions

1. Download and install **Arduino IDE** from [arduino.cc](https://www.arduino.cc/en/software)
2. Open Arduino IDE
3. Go to **File → Open** and select `robot_arm/robot_arm.ino`
4. Connect the Arduino to your laptop via USB
5. In the IDE, go to **Tools → Board** and select **Arduino Uno** (or your board)
6. Go to **Tools → Port** and select the COM port your Arduino is on (e.g. `COM9`)
   > On Windows: open **Device Manager → Ports (COM & LPT)** to confirm the COM port
7. Click the **Upload (→)** button
8. Wait for `Done uploading.` to appear in the status bar
9. **Close** the Arduino IDE Serial Monitor (if open) — it must be closed before running the Python script

---

## 💻 PC Setup: Step-by-Step

### Step 1: Clone the Repository
```bash
git clone https://github.com/geniusalert/robotic-arm.git
cd "robotic arm/robotic_sorting_system"
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```
This installs: `ultralytics` (YOLOv8), `opencv-python`, `pyserial`, `Pillow`

### Step 3: Configure Settings
Open `config.py` and verify/update:

```python
COM_PORT      = "COM9"    # ← Match your Arduino's COM port (check Device Manager)
CAMERA_INDEX  = 1         # ← 1 = external USB webcam, 0 = built-in laptop cam
CAMERA_FPS    = 8         # ← USB2.0 PC CAMERA native FPS
CAMERA_WIDTH  = 1280      # ← Camera resolution width
CAMERA_HEIGHT = 720       # ← Camera resolution height
LEFT_THRESHOLD  = 200     # ← Pixel X boundary for Left zone
RIGHT_THRESHOLD = 400     # ← Pixel X boundary for Right zone
CONFIDENCE_THRESHOLD = 0.35  # ← Detection confidence (lower = more sensitive)
DEBUG_MODE    = True      # ← Set False to enable real arm control
```

> **Finding your COM port**: In Windows, open **Device Manager → Ports (COM & LPT)**. The Arduino shows as `USB Serial Device (COMx)`.

### Step 4: Validate Camera Configuration (if needed)
If the camera doesn't open properly, run:
```bash
python diagnose_camera.py
```
This utility checks all camera indices and attempts to read frames to verify resolutions. Update `CAMERA_INDEX` in `config.py` to the one showing `1280x720`.

### Step 5: Test Hardware Manually
Before running AI, verify everything works:
```bash
python gui_test.py
```
- Top panel: live webcam feed
- Bottom panel: logs showing `Camera OK` and `Connected to COMx`
- Click **Pick Left / Center / Right** buttons — the arm should physically move and drop

### Step 6: Run the Autonomous AI System
Once hardware is verified:
```bash
python main.py
```

**What happens:**
1. Connects to Arduino on the configured COM port
2. Loads the YOLOv8 model (downloads ~6 MB on first run)
3. Opens the external webcam (`USB2.0 PC CAMERA` at 1280×720 @ 8 FPS)
4. Live window opens showing the camera feed with zone dividers (blue vertical lines)

**In Debug Mode** (`DEBUG_MODE = True`):
- All detected objects are shown with grey/green bounding boxes and labels
- Cyan text at top shows detection count
- Arm does **not** move — use this to verify detection is working

**In Live Mode** (`DEBUG_MODE = False`):
- Only oranges trigger arm movement
- Orange bounding box + zone label shown
- Command (`L` / `C` / `R`) sent to Arduino every `COMMAND_DELAY` seconds

Press **ESC** to exit safely.

---

## 🔁 Full System Flow

```
[USB2.0 Webcam] → frame
        ↓
[YOLOv8 Model] → detects orange + bounding box
        ↓
[Zone Classifier] → center_x < 200? → L | 200-400? → C | > 400? → R
        ↓
[serial_comm.py] → sends "L" / "C" / "R" over USB Serial
        ↓
[Arduino (robot_arm.ino)] → pick_left/center/right → drop_object → goHome
        ↓
[4 Servo Motors] → physical arm movement
```

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---------|-----|
| `No module named 'serial'` | Run `pip install pyserial` |
| `Error opening serial port COMx` | Check COM port in Device Manager, update `COM_PORT` in `config.py`. Close Arduino IDE Serial Monitor if open. |
| Camera opens but no frame | Run `diagnose_camera.py` or `scan_cameras.py` to find correct index. Verify no other app is using the webcam. |
| Camera loads laptop face cam | Ensure `CAMERA_INDEX = 1` in `config.py`. Index `0` is typically the laptop's built-in webcam. |
| No objects detected | Enable `DEBUG_MODE = True`, lower `CONFIDENCE_THRESHOLD` to `0.25`, ensure good lighting |
| Arm moves erratically | Confirm shared GND between Arduino and external servo power supply |
| `yolov8n.pt` not found | Runs automatically on first launch. Ensure internet connection. |
