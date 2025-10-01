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
  const [dimensions, setDimensions] = useState(null);
  const [dimLoading, setDimLoading] = useState(false);
  const [binInfo, setBinInfo] = useState(null);
  const [binLoading, setBinLoading] = useState(false);

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

  const handleCalculateDimensions = async () => {
    setDimLoading(true);
    setError(null);
    setDimensions(null);
    //setBinInfo(null); // Optionally clear previous bin info
    try {
      const response = await fetch(
        "http://localhost:8000/calculate-dimensions",
        {
          method: "POST",
        }
      );
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      const data = await response.json();
      setDimensions(data.dimensions || []);
      setBinInfo(data.bin_contents || null);
    } catch (err) {
      setError(err.message);
    } finally {
      setDimLoading(false);
    }
  };

  const handleGetBinInfo = async () => {
    setBinLoading(true);
    setError(null);
    setBinInfo(null);
    try {
      const response = await fetch("http://localhost:8000/bin-info");
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      const data = await response.json();
      setBinInfo(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setBinLoading(false);
    }
  };

  const handleRunAll = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    setDimensions(null);
    setBinInfo(null);

    try {
      // 1. Run model
      let response = await fetch("http://localhost:8000/run-model", {
        method: "POST",
      });
      if (!response.ok) throw new Error("Run Model failed");
      let data = await response.json();
      setResult(data);

      // 2. Calculate dimensions
      response = await fetch("http://localhost:8000/calculate-dimensions", {
        method: "POST",
      });
      if (!response.ok) throw new Error("Calculate Dimensions failed");
      data = await response.json();
      setDimensions(data.dimensions || []);
      setBinInfo(data.bin_contents || null); // This updates the pie chart!
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="App-header">3D Bin Packing Demo</div>

      {/* Run All button on top */}
      <div style={{ marginBottom: "1em" }}>
        <button
          onClick={handleRunAll}
          disabled={loading}
          className="run-all-button"
        >
          {loading ? "Processing..." : "Run Model, Dimensions & Update Bin"}
        </button>
      </div>

      {/* Other buttons below */}
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
      <button
        onClick={handleCalculateDimensions}
        style={{ marginLeft: "1em" }}
        disabled={dimLoading}
      >
        {dimLoading ? "Calculating..." : "Calculate Dimensions"}
      </button>
      <button
        onClick={handleGetBinInfo}
        style={{ marginLeft: "1em" }}
        disabled={binLoading}
      >
        {binLoading ? "Loading..." : "Get Bin Info"}
      </button>
      {dimensions && dimensions.length > 0 && (
        <div>
          <h3>Objects Detected:</h3>
          <ul>
            {dimensions.map((obj) => (
              <li key={obj.detection_id}>
                {obj.class} ({obj.closest_match?.label || "?"}) – Estimated
                Dimensions: {obj.width_m.toFixed(3)}m ×{" "}
                {obj.height_m.toFixed(3)}m
              </li>
            ))}
          </ul>
        </div>
      )}
      <PieChartExample binInfo={binInfo} />
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
      {dimensions && (
        <div>
          <h3>Calculated Dimensions:</h3>
          <pre className="json-output">
            {JSON.stringify(dimensions, null, 2)}
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
      {binInfo && (
        <div>
          <h3>Bin Info:</h3>
          <pre className="json-output">{JSON.stringify(binInfo, null, 2)}</pre>
        </div>
      )}
    </>
  );
}

export default App;
