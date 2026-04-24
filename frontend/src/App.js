import React, { useState } from "react";
import axios from "axios";
import "./App.css";
const API = process.env.REACT_APP_API_URL;
function App() {
  const [topic, setTopic] = useState("");
  const [tone, setTone] = useState("Professional");
  const [audience, setAudience] = useState("");
  const [loading, setLoading] = useState(false);
  const [approved, setApproved] = useState(false);
  const [result, setResult] = useState(null);
  const [activeTab, setActiveTab] = useState("instagram");

  const generateContent = async () => {
    setLoading(true);
    setApproved(false);
    setResult(null);

    try {
      const response = await axios.post("http://localhost:5000/generate", {
        topic,
        tone,
        audience,
      });

      setResult(response.data);
    } catch (error) {
      alert("Backend not running.");
    }

    setLoading(false);
  };

  const downloadPDF = async () => {
  const response = await axios.post(
    "http://localhost:5000/download-pdf",
    result,
    { responseType: "blob" }
  );

  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");

  link.href = url;
  link.setAttribute("download", "content_report.pdf");

  document.body.appendChild(link);
  link.click();
};

  const tabTitle = {
    instagram: "Instagram Caption",
    linkedin: "LinkedIn Post",
    article: "LinkedIn Article",
    twitter: "Twitter Thread",
  };

  return (
    <div className="page">

      <div className="wrapper">

        <header className="hero">
          <h1>Multi-Agent Social Media Content Generator</h1>
          <p>Generate Posts, Articles and Threads</p>
        </header>

        <section className="panel">

          <div className="grid-form">

            <div className="field">
              <label>Topic</label>
              <input
                type="text"
                placeholder="Ex: Dance"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
              />
            </div>

            <div className="field">
              <label>Tone</label>
              <select
                value={tone}
                onChange={(e) => setTone(e.target.value)}
              >
                <option>Professional</option>
                <option>Energetic</option>
                <option>Motivational</option>
                <option>Funny</option>
              </select>
            </div>

            <div className="field">
              <label>Audience</label>
              <input
                type="text"
                placeholder="Ex: Youth"
                value={audience}
                onChange={(e) => setAudience(e.target.value)}
              />
            </div>

          </div>

          <button
            className="primary-btn"
            onClick={generateContent}
            disabled={loading}
          >
            {loading ? "Generating..." : "Generate Content"}
          </button>

          {loading && (
            <div className="loader-wrap">
              <div className="loader"></div>
              <p>Generating fresh content...</p>
            </div>
          )}

        </section>

        {result && !loading && (
          <>
            <section className="tabs">
              <button onClick={() => setActiveTab("instagram")}>Instagram</button>
              <button onClick={() => setActiveTab("linkedin")}>LinkedIn</button>
              <button onClick={() => setActiveTab("article")}>Article</button>
              <button onClick={() => setActiveTab("twitter")}>Twitter</button>
            </section>

            <section className="result-card">
              <h2>{tabTitle[activeTab]}</h2>
              <p>{result[activeTab]}</p>
            </section>

            <section className="actions">
              <button onClick={() => setApproved(true)}>Approve</button>
              <button onClick={generateContent}>Regenerate</button>

              {approved && (
                <button onClick={downloadPDF}>
                  Download PDF
                </button>
              )}
            </section>
          </>
        )}

      </div>
    </div>
  );
}

export default App;