import pyrealsense2 as rs
import time

# Create pipeline and config
pipeline = rs.pipeline()
config = rs.config()

# Enable depth and color streams
config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)

# Record to file
config.enable_record_to_file("output.bag")

# Start pipeline
pipeline.start(config)

try:
    print("Recording for 5 seconds...")
    start_time = time.time()
    while time.time() - start_time < 2:
        frames = pipeline.wait_for_frames()
        # (Optional) Process frames here if needed
finally:
    pipeline.stop()
    print("Recording complete. Saved to output.bag")
