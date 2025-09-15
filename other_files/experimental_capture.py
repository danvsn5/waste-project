import cv2
import numpy as np
from PIL import Image

# Replace with your filenames (make sure they match from the capture step)
rgb_path = "frames/rgb_0_20250904.png"
depth_path = "frames/depth_raw_0_20250904.png"

# Load images
rgb_image = cv2.imread(rgb_path)
depth_raw = np.array(Image.open(depth_path))  # 16-bit depth values

def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        depth_value = depth_raw[y, x]  # in millimeters
        print(f"Clicked at ({x}, {y}) → {depth_value} mm")

# Show RGB image and set mouse callback
cv2.imshow("RGB Image - Click to query depth", rgb_image)
cv2.setMouseCallback("RGB Image - Click to query depth", mouse_callback)

print("Click anywhere on the RGB image to see depth in mm. Press any key to exit.")
cv2.waitKey(0)
cv2.destroyAllWindows()
