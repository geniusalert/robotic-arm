import cv2
import numpy as np
from ultralytics import YOLO
from config import CONFIDENCE_THRESHOLD, TARGET_MODE, TARGET_CLASS, TARGET_COLOR

model = None

def init_vision():
    """
    Initializes the vision system based on TARGET_MODE.
    """
    global model
    if TARGET_MODE == "yolo":
        print("Loading YOLOv8 model...")
        model = YOLO("yolov8n.pt")  # Use YOLOv8 nano for speed
        print("YOLOv8 Model loaded.")
    else:
        print(f"Vision initialized in COLOR mode. Targeting: {TARGET_COLOR.upper()}")

def get_color_bounds(color_name):
    """
    Returns the lower and upper HSV bounds for the specified color.
    Red requires two ranges because it wraps around the HSV cylinder.
    """
    color = color_name.lower().strip()
    if color == "red":
        return [
            (np.array([0, 120, 70]), np.array([10, 255, 255])),
            (np.array([170, 120, 70]), np.array([180, 255, 255]))
        ]
    elif color == "green":
        return [(np.array([40, 40, 40]), np.array([80, 255, 255]))]
    elif color == "blue":
        return [(np.array([100, 150, 0]), np.array([140, 255, 255]))]
    elif color == "yellow":
        return [(np.array([20, 100, 100]), np.array([30, 255, 255]))]
    else:
        # Default fallback to red
        return [(np.array([0, 120, 70]), np.array([10, 255, 255]))]

def detect_objects(frame):
    """
    Routes the detection to either color tracking or YOLO tracking.
    Returns:
        label (str): Class name or Color name
        bbox (tuple): (x1, y1, x2, y2)
        center_x (int): Horizontal center of the bounding box
    """
    if TARGET_MODE == "color":
        return detect_color_hsv(frame)
    else:
        return detect_yolo(frame)

def detect_color_hsv(frame):
    """
    Finds the largest contour of the target color using HSV thresholding.
    """
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    bounds = get_color_bounds(TARGET_COLOR)
    
    # Create mask combining all bounds
    mask = np.zeros(hsv_frame.shape[:2], dtype=np.uint8)
    for lower, upper in bounds:
        mask = cv2.bitwise_or(mask, cv2.inRange(hsv_frame, lower, upper))
        
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    best_area = 0
    best_det = None
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 500 and area > best_area:  # Minimum area threshold
            best_area = area
            x, y, w, h = cv2.boundingRect(cnt)
            center_x = x + (w // 2)
            label = f"{TARGET_COLOR.capitalize()} Object"
            best_det = (label, (x, y, x + w, y + h), center_x)
            
    return best_det if best_det else (None, None, None)

def detect_yolo(frame):
    """
    Detects objects using YOLO and filters for TARGET_CLASS.
    """
    if model is None:
        return None, None, None
        
    results = model(frame, verbose=False)
    
    best_conf = 0.0
    best_det = None
    
    for r in results:
        boxes = r.boxes
        for box in boxes:
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            label = model.names[cls]
            
            # Filter for target class with confidence threshold
            if label.lower() == TARGET_CLASS.lower() and conf > CONFIDENCE_THRESHOLD:
                if conf > best_conf:
                    best_conf = conf
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    center_x = (x1 + x2) // 2
                    best_det = (label.capitalize(), (x1, y1, x2, y2), center_x)
                    
    return best_det if best_det else (None, None, None)

def draw_debug_detections(frame):
    """
    DEBUG MODE: Draws ALL detected objects on frame or color masks.
    """
    if TARGET_MODE == "color":
        bounds = get_color_bounds(TARGET_COLOR)
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        for lower, upper in bounds:
            mask = cv2.bitwise_or(mask, cv2.inRange(hsv_frame, lower, upper))
            
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        count = 0
        for cnt in contours:
            if cv2.contourArea(cnt) > 500:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, f"{TARGET_COLOR.capitalize()} Area", (x, y - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)
                count += 1
                
        cv2.putText(frame, f"[DEBUG] {count} {TARGET_COLOR.capitalize()} object(s) detected", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)
        return frame
    
    else:
        # Original YOLO debug drawing
        if model is None:
            return frame

        results = model(frame, verbose=False)
        count = 0

        for r in results:
            boxes = r.boxes
            for box in boxes:
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                label = model.names[cls]

                if conf > 0.25:  # Low threshold to show everything
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    color = (0, 255, 0) if label.lower() == TARGET_CLASS.lower() else (200, 200, 200)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 8),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
                    count += 1

        # Show total detection count in top-left corner
        cv2.putText(frame, f"[DEBUG] {count} object(s) detected", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)
        return frame
