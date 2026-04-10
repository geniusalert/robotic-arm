"""
Camera Scanner Utility
Run this to find which index your external webcam is on.
"""
import cv2

print("Scanning for available cameras (indices 0-4)...\n")
found = []

for i in range(5):
    # Use CAP_DSHOW for reliable detection on Windows
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret and frame is not None:
            h, w = frame.shape[:2]
            print(f"  [FOUND] Camera index {i} — resolution {w}x{h}")
            found.append(i)
        else:
            print(f"  [OPEN but NO FRAME] Camera index {i}")
        cap.release()
    else:
        print(f"  [NOT FOUND] Camera index {i}")

print()
if found:
    print(f"Working cameras: {found}")
    print(f"Set CAMERA_INDEX = {found[-1]} in config.py for external webcam (usually the last one).")
else:
    print("No working cameras found. Check your USB connection.")
