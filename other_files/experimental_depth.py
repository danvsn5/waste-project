import json
import numpy as np
from PIL import Image, ImageDraw
import pyrealsense2 as rs

# ----------------------------
# User inputs
# ----------------------------
json_path = "newjson.json"       # YOLO JSON file
depth_path = "frames/depth_raw_1_20250904.png"  # aligned depth
rgb_path  = "frames/rgb_1_20250904.png"        # optional for visualization

# ----------------------------
# Load depth image
# ----------------------------
depth_image = np.array(Image.open(depth_path))  # 16-bit depth in mm
image_height, image_width = depth_image.shape

# Optional: RGB for visualization
rgb_image = np.array(Image.open(rgb_path))

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
# Helper function to create mask from polygon
# ----------------------------
def polygon_to_mask(polygon, height, width):
    mask_img = Image.new('L', (width, height), 0)
    polygon_pts = [(int(x), int(y)) for x, y in polygon]
    ImageDraw.Draw(mask_img).polygon(polygon_pts, outline=1, fill=1)
    mask = np.array(mask_img, dtype=bool)
    return mask

# ----------------------------
# Process each object
# ----------------------------
for obj in pred_list:
    obj_id = obj.get("detection_id", None)
    obj_class = obj.get("class", "unknown")
    
    # Extract polygon points
    polygon_pts = [(p["x"], p["y"]) for p in obj["points"]]

    # Create mask
    mask = polygon_to_mask(polygon_pts, image_height, image_width)

    # Extract depth values
    depth_values = depth_image[mask]
    depth_valid = depth_values[depth_values > 0]
    if len(depth_valid) == 0:
        print(f"Object {obj_id} ({obj_class}): no valid depth, skipping.")
        continue

    # Average depth in meters
    avg_depth_m = np.mean(depth_valid) / 1000.0

    # Pixel width/height
    ys, xs = np.where(mask)
    width_px = xs.max() - xs.min()
    height_px = ys.max() - ys.min()

    # Convert to real-world dimensions
    width_m = width_px * avg_depth_m / fx
    height_m = height_px * avg_depth_m / fy

    print(f"Object {obj_id} ({obj_class}): width ≈ {width_m:.3f} m, height ≈ {height_m:.3f} m")
