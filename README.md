# 🏗️ Waste Detection System

This project is a proof-of-concept system designed to detect and classify construction waste using RGB and depth data from a RealSense camera, object detection via Roboflow, and a web frontend to display results.

---

## 🔧 Backend Setup

To setup:

```bash
cd backend
pip install -r requirements.txt
```

Create a .env file inside the backend/ folder with the following contents:

```ROBOFLOW_API_URL=https://detect.roboflow.com
ROBOFLOW_API_KEY=your_api_key_here
WORKSPACE_NAME=your_workspace_name
WORKFLOW_ID=your_workflow_i
```

## 🔧 Frontend Setup

To setup:

```
cd frontend
npm install
```

To run:

```
npm run dev
```
