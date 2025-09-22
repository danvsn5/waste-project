import pyrealsense2 as rs
import numpy as np
from PIL import Image
import os
from datetime import datetime
import winsound  # Windows only

# Create output folder
os.makedirs("frames", exist_ok=True)

# Configure pipeline
pipeline = rs.pipeline()
config = rs.config()

# Enable depth and color streams
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)

# Start streaming
pipeline.start(config)

# Create align object (align depth to color)
align_to = rs.stream.color
align = rs.align(align_to)

# Depth colorizer (for visualization)
colorizer = rs.colorizer()

# Image counter
image_number = 1

try:
    print("Press Enter to capture (RGB + aligned depth), or type 'q' then Enter to quit.")
    while True:
        user_input = input()
        if user_input.lower() == "q":
            break

        # Wait for frames and align
        frames = pipeline.wait_for_frames()
        aligned_frames = align.process(frames)

        # Get aligned frames
        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        if depth_frame and color_frame:
            # Convert to numpy arrays
            depth_image = np.asanyarray(depth_frame.get_data())        # Raw aligned depth
            color_image = np.asanyarray(color_frame.get_data())        # BGR
            colorized_depth = np.asanyarray(colorizer.colorize(depth_frame).get_data())  # Colored depth

            # Convert BGR to RGB
            color_image = color_image[:, :, ::-1]
            colorized_depth = colorized_depth[:, :, ::-1]

            # Timestamp
            date_str = datetime.now().strftime("%Y%m%d")

            # Save RGB
            rgb_filename = os.path.join("frames", f"rgb_{image_number}_{date_str}.png")
            Image.fromarray(color_image).save(rgb_filename)

            # Save raw aligned depth (16-bit PNG)
            depth_filename = os.path.join("frames", f"depth_raw_{image_number}_{date_str}.png")
            Image.fromarray(depth_image).save(depth_filename)

            # Save colorized aligned depth (for visualization)
            depth_vis_filename = os.path.join("frames", f"depth_vis_{image_number}_{date_str}.png")
            Image.fromarray(colorized_depth).save(depth_vis_filename)

            print(f"Saved {rgb_filename}, {depth_filename}, {depth_vis_filename}")
            winsound.Beep(1000, 200)
            image_number += 1

except KeyboardInterrupt:
    print("Stopped capturing images.")

finally:
    pipeline.stop()
