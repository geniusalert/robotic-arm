import cv2
from ultralytics import YOLO
from config import CONFIDENCE_THRESHOLD

model = None

def init_vision():
    """
    Loads the YOLOv8 model for object detection.
    """
    global model
    print("Loading YOLOv8 model...")
    model = YOLO("yolov8n.pt")  # Use YOLOv8 nano for speed
    print("Model loaded.")

def detect_objects(frame):
    """
    Detects objects and filters for 'orange' with specific confidence.
    Returns:
        label (str): Class name
        bbox (tuple): (x1, y1, x2, y2)
        center_x (int): Horizontal center of the bounding box
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
            
            # Filter for orange with confidence threshold
            if label.lower() == 'orange' and conf > CONFIDENCE_THRESHOLD:
                if conf > best_conf:
                    best_conf = conf
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    center_x = (x1 + x2) // 2
                    best_det = (label, (x1, y1, x2, y2), center_x)
                    
    if best_det:
        return best_det
        
    return None, None, None

def draw_debug_detections(frame):
    """
    DEBUG MODE: Draws ALL detected objects on frame regardless of class.
    Helps verify the model is working and camera is seeing things correctly.
    """
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
                color = (0, 255, 0) if label.lower() == 'orange' else (200, 200, 200)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
                count += 1

    # Show total detection count in top-left corner
    cv2.putText(frame, f"[DEBUG] {count} object(s) detected", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)
    return frame
