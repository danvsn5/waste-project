import json
import numpy as np
from PIL import Image
import cv2
import pyrealsense2 as rs

# ----------------------------
# User inputs
# ----------------------------
json_path = "newjson.json"
depth_path = "frames/depth_raw_0_20250904.png"

# ----------------------------
# Load depth image
# ----------------------------
depth_image = np.array(Image.open(depth_path))  # 16-bit depth in mm
image_height, image_width = depth_image.shape

# ----------------------------
# Load YOLO JSON
# ----------------------------
with open(json_path, 'r') as f:
    data = json.load(f)

pred_list = data["results"]["image.png"][0]["detection_predictions"]["predictions"]

# ----------------------------
# Get camera intrinsics
# ----------------------------
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
profile = pipeline.start(config)
intr = profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()
fx, fy = intr.fx, intr.fy
pipeline.stop()

# ----------------------------
# Process each object
# ----------------------------
for obj in pred_list:
    obj_id = obj.get("detection_id", None)
    obj_class = obj.get("class", "unknown")
    
    # Extract polygon points
    polygon_pts = np.array([[p["x"], p["y"]] for p in obj["points"]], dtype=np.float32)

    # Compute minimum area rectangle
    rect = cv2.minAreaRect(polygon_pts)
    (cx, cy), (width_px, height_px), angle = rect

    # Create a mask from polygon to extract depth
    mask_img = Image.new('L', (image_width, image_height), 0)
    cv_pts = [(int(x), int(y)) for x, y in polygon_pts]
    from PIL import ImageDraw
    ImageDraw.Draw(mask_img).polygon(cv_pts, outline=1, fill=1)
    mask = np.array(mask_img, dtype=bool)

    # Extract depth values
    depth_values = depth_image[mask]
    depth_valid = depth_values[depth_values > 0]
    if len(depth_valid) == 0:
        print(f"Object {obj_id} ({obj_class}): no valid depth, skipping.")
        continue

    avg_depth_m = np.mean(depth_valid) / 1000.0  # meters

    # Convert pixel width/height to meters
    width_m = width_px * avg_depth_m / fx
    height_m = height_px * avg_depth_m / fy

    print(f"Object {obj_id} ({obj_class}): width ≈ {width_m:.3f} m, length ≈ {height_m:.3f} m, angle = {angle:.1f}°")
