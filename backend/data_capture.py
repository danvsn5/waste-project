import pyrealsense2 as rs
import numpy as np
from PIL import Image
import os
from datetime import datetime

def capture_frames(output_folder="current_data"):
    # Ensure the folder is inside the backend directory
    backend_folder = os.path.join(os.path.dirname(__file__), output_folder)
    os.makedirs(backend_folder, exist_ok=True)

    # Configure pipeline
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)

    # Start streaming
    pipeline.start(config)

    # Align depth to color
    align_to = rs.stream.color
    align = rs.align(align_to)
    colorizer = rs.colorizer()

    # sleep for 2 seconds to allow camera to warm up
    import time
    time.sleep(2)

    try:
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
            date_str = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Save RGB
            rgb_filename = os.path.join(backend_folder, f"rgb_{date_str}.png")
            Image.fromarray(color_image).save(rgb_filename)

            # Save raw aligned depth (16-bit PNG)
            depth_filename = os.path.join(backend_folder, f"depth_raw_{date_str}.png")
            Image.fromarray(depth_image).save(depth_filename)

            # Save colorized aligned depth (for visualization)
            depth_vis_filename = os.path.join(backend_folder, f"depth_vis_{date_str}.png")
            Image.fromarray(colorized_depth).save(depth_vis_filename)

            return {
                "rgb": rgb_filename,
                "depth_raw": depth_filename,
                "depth_vis": depth_vis_filename
            }
        else:
            return {"error": "Could not capture frames from camera."}
    finally:
        pipeline.stop()