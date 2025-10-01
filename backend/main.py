import os
import json
from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from inference_sdk import InferenceHTTPClient
from dotenv import load_dotenv
from typing import Dict, Any
from object_tracker import process_detections
from data_capture import capture_frames
from fastapi.staticfiles import StaticFiles
from dimension_calculator import calculate_dimensions_for_objects

bin_state = []  # List of detected objects
new_objects = []  # List of newly detected objects in the latest run
bin_contents = {
    "timber": 0.0,  # volume in m^3
    "pipe": 0.0,
    "brick": 0.0
}

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = InferenceHTTPClient(
    api_url=os.getenv("ROBOFLOW_API_URL"),
    api_key=os.getenv("ROBOFLOW_API_KEY")
)

workspace_name = os.getenv("WORKSPACE_NAME")
workflow_id = os.getenv("WORKFLOW_ID")

# Serve the current_data folder as static files
app.mount("/current_data", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "current_data")), name="current_data")

@app.post("/run-model")
async def run_model():
    global new_objects
    images_folder = os.path.join(os.path.dirname(__file__), "current_data")
    all_results = {}
    new_objects = []

    # Only process RGB images in current_data folder
    for filename in os.listdir(images_folder):
        if filename.startswith("rgb_") and filename.lower().endswith(".png"):
            image_path = os.path.join(images_folder, filename)
            print(f"Processing {filename}...")

            try:
                result = client.run_workflow(
                    workspace_name=workspace_name,
                    workflow_id=workflow_id,
                    images={"image": image_path},
                    use_cache=True
                )
                all_results[filename] = result
                # Extract predictions and process them
                for detection_result in result:
                    preds = detection_result.get("detection_predictions", {}).get("predictions", [])
                    new_objs = process_detections(preds, bin_state)
                    new_objects.extend(new_objs)
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                all_results[filename] = {"error": str(e)}

    return JSONResponse(content={
        "message": "Model run completed",
        "results": all_results,
        "new_objects": new_objects,
        "bin_state": bin_state
    })

@app.post("/capture-data")
async def capture_data():
    output = capture_frames(output_folder="current_data")
    return JSONResponse(content=output)

@app.get("/list-current-data")
async def list_current_data():
    folder = os.path.join(os.path.dirname(__file__), "current_data")
    files = []
    for fname in os.listdir(folder):
        if fname.lower().endswith((".png", ".jpg", ".jpeg")):
            files.append({
                "filename": fname,
                "url": f"/current_data/{fname}"
            })
    return JSONResponse(content={"files": files})

@app.post("/calculate-dimensions")
async def calculate_dimensions():
    global new_objects, bin_contents
    folder = os.path.join(os.path.dirname(__file__), "current_data")
    depth_images = [f for f in os.listdir(folder) if f.startswith("depth_raw_") and f.endswith(".png")]
    if not depth_images:
        return JSONResponse(content={"error": "No depth image found."}, status_code=404)
    depth_images.sort(reverse=True)
    depth_image_path = os.path.join(folder, depth_images[0])

    if not new_objects:
        return JSONResponse(content={"error": "No new objects found."}, status_code=404)

    dims = calculate_dimensions_for_objects(new_objects, depth_image_path)

    # Update bin_contents and clear new_objects
    for obj in dims:
        obj_class = obj.get("class")
        width = obj.get("width_m")
        height = obj.get("height_m")
        if obj_class == "pipe":
            # Pipe: volume = π * (radius^2) * length (use width as length, 2.3cm diameter)
            radius = 0.023 / 2
            length = width if width > height else height
            volume = 3.14159 * (radius ** 2) * length
        else:
            # Other: volume = width * height * depth (depth = 0.05m)
            volume = width * height * 0.05
        bin_contents[obj_class] = bin_contents.get(obj_class, 0.0) + volume

    new_objects = []  # Clear after processing

    # Delete all images in current_data folder
    for filename in os.listdir(folder):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            file_path = os.path.join(folder, filename)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

    return JSONResponse(content={"dimensions": dims, "bin_contents": bin_contents})

@app.get("/bin-info")
async def get_bin_info():
    return JSONResponse(content=bin_contents)