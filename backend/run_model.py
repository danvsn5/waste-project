import os
import json
from inference_sdk import InferenceHTTPClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Roboflow client using environment variables
client = InferenceHTTPClient(
    api_url=os.getenv("ROBOFLOW_API_URL"),
    api_key=os.getenv("ROBOFLOW_API_KEY")
)

# Set workflow info
workspace_name = os.getenv("WORKSPACE_NAME")
workflow_id = os.getenv("WORKFLOW_ID")

# Path to your images folder
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

# Save results to a JSON file
output_path = "results.json"
with open(output_path, "w") as f:
    json.dump(all_results, f, indent=2)

print(f"\n✅ All results saved to '{output_path}'")
