COM_PORT = "COM9"
BAUD_RATE = 9600
LEFT_THRESHOLD = 200
RIGHT_THRESHOLD = 400
CONFIDENCE_THRESHOLD = 0.35  # Lowered for better detection sensitivity
COMMAND_DELAY = 2  # seconds delay between commands to prevent rapid triggering

# Camera index: 0 = built-in laptop cam, 1 = external USB webcam
# Change to 0 if you want to use the built-in camera instead
CAMERA_INDEX = 1

# USB2.0 PC CAMERA hardware settings
CAMERA_FPS    = 8      # Camera native FPS
CAMERA_WIDTH  = 1280   # Capture width
CAMERA_HEIGHT = 720    # Capture height

# Debug mode: shows ALL detected objects on screen (not just orange)
# Set to False once everything is working
DEBUG_MODE = True
