import numpy as np
from PIL import Image, ImageDraw
import cv2
import pyrealsense2 as rs
import os
from ground_truth_dimensions import GROUND_TRUTH_DIMENSIONS

def find_closest_match(obj_class, width, height):
    candidates = GROUND_TRUTH_DIMENSIONS.get(obj_class.lower(), [])
    if not candidates:
        return None
    # Find the candidate with the smallest Euclidean distance in (width, height) space
    closest = min(
        candidates,
        key=lambda c: ((c["width"] - width) ** 2 + (c["height"] - height) ** 2) ** 0.5
    )
    return closest

def get_camera_intrinsics():
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
    profile = pipeline.start(config)
    intr = profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()
    fx, fy = intr.fx, intr.fy
    pipeline.stop()
    return fx, fy

def compute_object_dimensions(obj, depth_image, fx, fy):
    # Extract polygon points
    polygon_pts = np.array([[p["x"], p["y"]] for p in obj["points"]], dtype=np.float32)
    image_height, image_width = depth_image.shape

    # Compute minimum area rectangle
    rect = cv2.minAreaRect(polygon_pts)
    (cx, cy), (width_px, height_px), angle = rect

    # Create a mask from polygon to extract depth
    mask_img = Image.new('L', (image_width, image_height), 0)
    cv_pts = [(int(x), int(y)) for x, y in polygon_pts]
    ImageDraw.Draw(mask_img).polygon(cv_pts, outline=1, fill=1)
    mask = np.array(mask_img, dtype=bool)

    # Extract depth values
    depth_values = depth_image[mask]
    depth_valid = depth_values[depth_values > 0]
    if len(depth_valid) == 0:
        return None

    avg_depth_m = np.mean(depth_valid) / 1000.0  # meters

    # Convert pixel width/height to meters
    width_m = width_px * avg_depth_m / fx
    height_m = height_px * avg_depth_m / fy

    return {
        "width_m": width_m,
        "height_m": height_m,
        "angle_deg": angle,
        "avg_depth_m": avg_depth_m
    }

def calculate_dimensions_for_objects(new_objects, depth_image_path):
    fx, fy = get_camera_intrinsics()
    depth_image = np.array(Image.open(depth_image_path))  # 16-bit depth in mm

    dimensions = []
    for obj in new_objects:
        dims = compute_object_dimensions(obj, depth_image, fx, fy)
        if dims:
            match = find_closest_match(obj.get("class"), dims["width_m"], dims["height_m"])
            dimensions.append({
                "detection_id": obj.get("detection_id"),
                "class": obj.get("class"),
                **dims,
                "closest_match": match
            })
    return dimensions