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

bin_state = []  # List of detected objects

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