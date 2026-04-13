"""
Camera Diagnostic Tool
Checks every camera index with multiple backends and reads actual frames.
"""
import cv2

print("=" * 60)
print("FULL CAMERA DIAGNOSTIC")
print("=" * 60)

for i in range(5):
    print(f"\n--- Camera Index {i} ---")
    
    # Try default backend
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        ret, frame = cap.read()
        if ret and frame is not None:
            actual_w, actual_h = frame.shape[1], frame.shape[0]
            print(f"  [DEFAULT] OPENED  | reported={w}x{h} | actual_frame={actual_w}x{actual_h}")
        else:
            print(f"  [DEFAULT] OPENED  | reported={w}x{h} | BUT CANNOT READ FRAME")
        cap.release()
    else:
        print(f"  [DEFAULT] CANNOT OPEN")

    # Try DSHOW backend
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
    if cap.isOpened():
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        ret, frame = cap.read()
        if ret and frame is not None:
            actual_w, actual_h = frame.shape[1], frame.shape[0]
            print(f"  [DSHOW]   OPENED  | reported={w}x{h} | actual_frame={actual_w}x{actual_h}")
        else:
            print(f"  [DSHOW]   OPENED  | reported={w}x{h} | BUT CANNOT READ FRAME")
        cap.release()
    else:
        print(f"  [DSHOW]   CANNOT OPEN")

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)
