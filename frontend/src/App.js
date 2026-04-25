import React, { useState } from "react";
import axios from "axios";
import "./App.css";

/* =====================================
   AUTO API URL
   Local -> localhost backend
   Deployed -> Railway backend from .env
===================================== */
const API =
  process.env.REACT_APP_API_URL || "http://127.0.0.1:5000";

function App() {
  const [topic, setTopic] = useState("");
  const [tone, setTone] = useState("Professional");
  const [audience, setAudience] = useState("");

  const [loading, setLoading] = useState(false);
  const [approved, setApproved] = useState(false);
  const [result, setResult] = useState(null);
  const [activeTab, setActiveTab] = useState("instagram");

  /* =====================================
     GENERATE CONTENT
  ===================================== */
  const generateContent = async () => {
  setLoading(true);
  setApproved(false);
  setResult(null);

  try {
    const response = await axios.post(`${API}/generate`, {
      topic,
      tone,
      audience,
    });

    setResult(response.data);

  } catch (error) {
    console.log("ERROR:", error.response?.data || error.message);

    alert(
      error.response?.data?.error ||
      "Backend request failed."
    );
  }

  setLoading(false);
};
  /* =====================================
     DOWNLOAD PDF
  ===================================== */
  const downloadPDF = async () => {
    try {
      const response = await axios.post(
        `${API}/download-pdf`,
        result,
        { responseType: "blob" }
      );

      const fileURL = window.URL.createObjectURL(
        new Blob([response.data])
      );

      const link = document.createElement("a");
      link.href = fileURL;
      link.setAttribute("download", "content_report.pdf");

      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.log(error);
      alert("PDF download failed.");
    }
  };

  /* =====================================
     TITLES
  ===================================== */
  const tabTitle = {
    instagram: "Instagram Caption",
    linkedin: "LinkedIn Post",
    article: "LinkedIn Article",
    twitter: "Twitter Thread",
  };

  return (
    <div className="page">
      <div className="wrapper">

        {/* HEADER */}
        <header className="hero">
          <h1>Multi-Agent Social Media Content Generator</h1>
          <p>Generate Posts, Articles and Threads</p>
        </header>

        {/* FORM */}
        <section className="panel">

          <div className="grid-form">

            {/* TOPIC */}
            <div className="field">
              <label>Topic</label>
              <input
                type="text"
                placeholder="Ex: Dance"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
              />
            </div>

            {/* TONE */}
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

            {/* AUDIENCE */}
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

          {/* BUTTON */}
          <button
            className="primary-btn"
            onClick={generateContent}
            disabled={loading}
          >
            {loading ? "Generating..." : "Generate Content"}
          </button>

          {/* LOADER */}
          {loading && (
            <div className="loader-wrap">
              <div className="loader"></div>
              <p>Generating fresh content...</p>
            </div>
          )}

        </section>

        {/* RESULT */}
        {result && !loading && (
          <>
            {/* TABS */}
            <section className="tabs">

              <button onClick={() => setActiveTab("instagram")}>
                Instagram
              </button>

              <button onClick={() => setActiveTab("linkedin")}>
                LinkedIn
              </button>

              <button onClick={() => setActiveTab("article")}>
                Article
              </button>

              <button onClick={() => setActiveTab("twitter")}>
                Twitter
              </button>

            </section>

            {/* CONTENT */}
            <section className="result-card">
              <h2>{tabTitle[activeTab]}</h2>
              <p>{result[activeTab]}</p>
            </section>

            {/* ACTIONS */}
            <section className="actions">

              <button onClick={() => setApproved(true)}>
                Approve
              </button>

              <button onClick={generateContent}>
                Regenerate
              </button>

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