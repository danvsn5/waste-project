import os
import json
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from inference_sdk import InferenceHTTPClient
from dotenv import load_dotenv

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

@app.post("/run-model")
async def run_model():
    images_folder = "images"
    all_results = {}

    for filename in os.listdir(images_folder):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
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
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                all_results[filename] = {"error": str(e)}

    return JSONResponse(content={"message": "Model run completed", "results": all_results})