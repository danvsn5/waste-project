import "./App.css";
import PieChartExample from "./components/PieChartExample.jsx";
import { useState } from "react";

function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null); // Add state for result

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
      setResult(data); // Save result to state
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button onClick={handleRunModel} disabled={loading}>
        {loading ? "Running..." : "Run Model"}
      </button>
      {error && <p>Error: {error}</p>}
      {result && (
        <div>
          <h3>Result:</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
      <PieChartExample />
    </>
  );
}

export default App;
