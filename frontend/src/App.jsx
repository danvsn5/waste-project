import "./App.css";
import PieChartExample from "./components/PieChartExample.jsx";
import { useState } from "react";

function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [captureResult, setCaptureResult] = useState(null);
  const [currentData, setCurrentData] = useState([]);
  const [listLoading, setListLoading] = useState(false);

  const handleRunModel = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await fetch("http://localhost:8000/run-model", {
        method: "POST",
      });
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCaptureData = async () => {
    setCaptureResult(null);
    setError(null);
    try {
      const response = await fetch("http://localhost:8000/capture-data", {
        method: "POST",
      });
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      const data = await response.json();
      setCaptureResult(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleListCurrentData = async () => {
    setListLoading(true);
    setError(null);
    setCurrentData([]);
    try {
      const response = await fetch("http://localhost:8000/list-current-data");
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      const data = await response.json();
      setCurrentData(data.files || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setListLoading(false);
    }
  };

  return (
    <>
      <button onClick={handleRunModel} disabled={loading}>
        {loading ? "Running..." : "Run Model"}
      </button>
      <button onClick={handleCaptureData} style={{ marginLeft: "1em" }}>
        Capture Data
      </button>
      <button
        onClick={handleListCurrentData}
        style={{ marginLeft: "1em" }}
        disabled={listLoading}
      >
        {listLoading ? "Loading..." : "List Current Data"}
      </button>
      {error && <p>Error: {error}</p>}
      {result && (
        <div>
          <h3>Result:</h3>
          <pre className="json-output">{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
      {captureResult && (
        <div>
          <h3>Capture Result:</h3>
          <pre className="json-output">
            {JSON.stringify(captureResult, null, 2)}
          </pre>
        </div>
      )}
      {currentData.length > 0 && (
        <div>
          <h3>Current Data Files:</h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "1em" }}>
            {currentData.map((file) => (
              <div key={file.filename} style={{ textAlign: "center" }}>
                <img
                  src={`http://localhost:8000${file.url}`}
                  alt={file.filename}
                  style={{
                    maxWidth: "200px",
                    maxHeight: "150px",
                    borderRadius: "8px",
                    border: "1px solid #ccc",
                  }}
                />
                <div>{file.filename}</div>
              </div>
            ))}
          </div>
        </div>
      )}
      <PieChartExample />
    </>
  );
}

export default App;
