import pyrealsense2 as rs
import numpy as np
from PIL import Image
import os
from datetime import datetime
import winsound  # For sound on Windows

# Create images directory if it doesn't exist
os.makedirs("mixed_images", exist_ok=True)

# Create pipeline and config
pipeline = rs.pipeline()
config = rs.config()

# Enable only the RGB color stream
config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)

# Start pipeline
pipeline.start(config)

# VERY IMPORTANT VARIABLE. CHANGE WHEN TAKING NEW IMAGES
image_number = 220

try:
    print("Press Enter to capture an image, or type 'q' then Enter to quit.")
    while True:
        user_input = input()
        if user_input.lower() == "q":
            break

        # Wait for the next frames
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()

        if color_frame:
            # Convert frame to numpy array
            color_image = np.asanyarray(color_frame.get_data())

            # Convert BGR to RGB
            color_image = color_image[:, :, ::-1]

            # Get current date (YYYYMMDD)
            date_str = datetime.now().strftime("%Y%m%d")

            # Create filename: test_<image_number>_<date>.png
            filename = os.path.join("mixed_images", f"mixed_{image_number}_{date_str}.png")

            # Save using Pillow
            Image.fromarray(color_image).save(filename)
            print(f"Saved {filename}")
            winsound.Beep(1000, 200)  # Frequency 1000Hz, Duration 200ms
            image_number += 1

except KeyboardInterrupt:
    print("Stopped capturing images.")

finally:
    pipeline.stop()
