# 🏗️ Waste Detection System

This project is a proof-of-concept system designed to detect and classify construction waste using RGB and depth data from a RealSense camera, object detection via Roboflow, and a web frontend to display results.

---

## 🔧 Backend Setup

To setup:

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file inside the `backend/` folder with the following contents:

```
ROBOFLOW_API_URL=https://detect.roboflow.com
ROBOFLOW_API_KEY=your_api_key_here
WORKSPACE_NAME=your_workspace_name
WORKFLOW_ID=your_workflow_id
```

### 🚀 Running the Backend Server

Start the FastAPI backend server with:

```bash
uvicorn main:app --reload
```

The backend will be available at [http://localhost:8000](http://localhost:8000).

---

## 🔧 Frontend Setup

To setup:

```bash
cd frontend
npm install
```

To run:

```bash
npm run dev
```

The frontend will be available at [http://localhost:5173](http://localhost:5173).

---

## 📝 Notes

- Make sure to restart the backend server after changing environment variables or backend code.
- The backend and frontend must be running simultaneously for full funcionality
