import { useState, useRef } from "react";
import ReactMarkdown from "react-markdown";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");

  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState("");
  const [contextScore, setContextScore] = useState("");
  const [answerScore, setAnswerScore] = useState("");
  const [faithfulnessScore, setFaithfulnessScore] = useState("");

  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);

  const [file, setFile] = useState(null);
  const [uploadMessage, setUploadMessage] = useState("");
  const [documents, setDocuments] = useState([]);
  const [chatHistory, setChatHistory] = useState([]);
  const [uploadStatus, setUploadStatus] = useState("");
  const [questionError, setQuestionError] = useState("");
  const fileInputRef = useRef(null);
  // Ask a question
  const askQuestion = async () => {
    if (!question.trim()) {
      setQuestionError("Please enter a question");
      return;
    }

    if (documents.length === 0) {
      return;
    }

    const currentQuestion = question.trim();

    setLoading(true);

    setAnswer("");
    setSources("");
    setContextScore("");
    setAnswerScore("");
    setFaithfulnessScore("");
    setUploadMessage("");

    try {
      const response = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: currentQuestion,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setAnswer(data.detail || "Failed to get answer.");
        return;
      }

      setAnswer(data.answer || "");
      setSources(data.sources || "");
      setContextScore(data.context_score || "");
      setAnswerScore(data.answer_score || "");
      setFaithfulnessScore(data.faithfulness_score || "");

      // Save complete conversation
      setChatHistory((previousHistory) => [
        ...previousHistory,
        {
          question: currentQuestion,
          answer: data.answer || "",
          sources: data.sources || "",
          contextScore: data.context_score || "",
          answerScore: data.answer_score || "",
          faithfulnessScore: data.faithfulness_score || "",
          agentProcess: data.process || [],
        },
      ]);

      setQuestion("");
      setQuestionError("");

    } catch (error) {
      console.error(error);
      setAnswer("Unable to connect to the backend.");

    } finally {
      setLoading(false);
    }
  };

  // Upload PDF
  const uploadPDF = async () => {
    if (!file) {
      setUploadMessage("Please select a PDF first.");
      return;
    }
    if (
      file.type !== "application/pdf" &&
      !file.name.toLowerCase().endsWith(".pdf")
    ) {
      setUploadMessage("Please upload a PDF file.");
      setUploadStatus("Upload failed.");
      return;
    }
    if (uploading) {
      return;
    }

    setUploading(true);
    setUploadStatus("Uploading PDF...");
    const formData = new FormData();
    formData.append("files", file);
    await new Promise((resolve) => setTimeout(resolve, 500));


    setUploadStatus("Processing PDF...");
    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        setUploadMessage(data.detail || "Upload failed.");
        setUploadStatus("Upload failed.");
        return;
      }

      setUploadMessage(
        `${data.message}. ${data.chunks_added} chunks added.`
      );

      if (data.files) {
        setDocuments((previousDocuments) => {
          const newDocuments = [...previousDocuments];

          data.files.forEach((uploadedFile) => {
            if (!newDocuments.includes(uploadedFile)) {
              newDocuments.push(uploadedFile);
            }
          });
          return newDocuments;
        });
      }
      setUploadStatus("PDF ready ✓");
      // Clear selected file
      setFile(null);

    } catch (error) {
      console.error(error);
      setUploadMessage("Error connecting to the backend.");
      setUploadStatus("Upload failed.");

    } finally {
      setUploading(false);
    }
  };

  // Clear documents
  const clearDocuments = async () => {
    const confirmClear=window.confirm(
      "Are you sure you want to clear all documents and chat history?"
    );
    if(!confirm){
      return;
    }
    try {
      const response = await fetch("http://localhost:8000/clear", {
        method: "DELETE",
      });

      const data = await response.json();

      if (!response.ok) {
        setUploadMessage("Failed to clear documents.");
        return;
      }

      setDocuments([]);
      setChatHistory([]);

      setAnswer("");
      setSources("");
      setContextScore("");
      setAnswerScore("");
      setFaithfulnessScore("");
      setQuestion("");
      setUploadStatus("");
      setFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
      setUploadMessage(
        data.message || "Documents cleared successfully."
      );

    } catch (error) {
      console.error(error);
      setUploadMessage("Error connecting to the backend.");
    }
  };

  return (
    <div className="app">
      <div className="container">

        {/* Header */}
        <header className="header">
          <h1>Agentic RAG Research Assistant</h1>

          <p>
            Ask questions about your research papers and get
            grounded answers with sources.
          </p>
        </header>

        {/* Upload Section */}
        <div className="upload-section">
          <h2>Upload Research Paper</h2>
          <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,application/pdf"
          onChange={(e) => {
            const selectedFile = e.target.files[0];

            if (!selectedFile) {
              return;
            }

            if (
              selectedFile.type !== "application/pdf" &&
              !selectedFile.name.toLowerCase().endsWith(".pdf")
            ) {
              setFile(null);
              setUploadMessage("Please upload a PDF file.");

              if (fileInputRef.current) {
                fileInputRef.current.value = "";
              }

              return;
            }

            setFile(selectedFile);
            setUploadMessage("");
          }}
          disabled={uploading}
        />

          <button
            type="button"
            onClick={uploadPDF}
            disabled={uploading}
          >
            {uploading ? "Uploading..." : "Upload PDF"}
          </button>
          {uploadMessage && (
  <p className="upload-message">
    {uploadMessage}
  </p>
)}
        </div>
        {uploadStatus && (
          <p className="upload-status">
            {uploadStatus}
          </p>
        )}
        {/* Documents Section */}
        <div className="documents-section">
          <div className="documents-header">
            <h2>Documents</h2>

            <button
              onClick={clearDocuments}
              disabled={
                documents.length === 0 || uploading
              }
            >
              Clear Documents
            </button>
          </div>

          {documents.length === 0 ? (
            <p className="empty-documents">
              No documents uploaded yet.
            </p>
          ) : (
            <div className="document-list">
              {documents.map((document, index) => (
                <div
                  className="document-item"
                  key={index}
                >
                  ✓ {document}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Loading */}
        {loading && (
          <div className="loading">
            Research agent is working...
          </div>
        )}


        {/* Chat History */}
        {chatHistory.length > 0 && (
          <div className="chat-history">

            {chatHistory.map((chat, index) => (
              <div
                className="content-grid"
                key={index}
              >

                {/* Answer */}
                <main className="answer-card">

                  <div className="question">
                    <h3>You</h3>
                    <p>{chat.question}</p>
                  </div>

                  <hr />

                  <h2>Answer</h2>

                  <div className="answer">
                    <ReactMarkdown>
                      {chat.answer}
                    </ReactMarkdown>
                  </div>

                </main>

                {/* Right Panel */}
                <aside className="side-panel">

                  {/* Agent Process */}
                  <div className="info-card">
                    <h3>Agent Process</h3>

                    <div className="agent-process">
                      {chat.agentProcess &&
                      chat.agentProcess.length > 0 ? (
                        chat.agentProcess.map(
                          (step, stepIndex) => (
                            <div
                              className="process-step"
                              key={stepIndex}
                            >
                              {step}
                            </div>
                          )
                        )
                      ) : (
                        <p>No process information available.</p>
                      )}
                    </div>
                  </div>

                  {/* Evaluation */}
                  <div className="info-card">
                    <h3>Evaluation</h3>

                    <div className="score">
                      <span>Context Relevance</span>
                      <strong>
                        {chat.contextScore || "N/A"}
                      </strong>
                    </div>

                    <div className="score">
                      <span>Answer Relevance</span>
                      <strong>
                        {chat.answerScore || "N/A"}
                      </strong>
                    </div>

                    <div className="score">
                      <span>Faithfulness</span>
                      <strong>
                        {chat.faithfulnessScore || "N/A"}
                      </strong>
                    </div>
                  </div>

                  {/* Sources */}
                  <div className="info-card">
                    <h3>Sources</h3>

                    <div className="sources">
                      {chat.sources ? (
                        chat.sources
                          .split("\n")
                          .map(
                            (source, sourceIndex) => (
                              <p key={sourceIndex}>
                                {source}
                              </p>
                            )
                          )
                      ) : (
                        <p>No sources available.</p>
                      )}
                    </div>
                  </div>

                </aside>

              </div>
            ))}

          </div>
        )}

        {/* Question Section - stays at bottom */}
        <div className="question-card">
          <input
            type="text"
            placeholder={
              documents.length === 0
                ? "Upload a research paper first..."
                : "Ask a question about your research papers..."
            }
            value={question}
            onChange={(e) => {
              setQuestion(e.target.value);
              setQuestionError("");
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                askQuestion();
              }
            }}
            disabled={
              documents.length === 0 || loading
            }
          />

          <button
            onClick={askQuestion}
            disabled={
              loading ||
              uploading ||
              documents.length === 0
            }
          >
            {loading ? "Searching..." : "Ask"}
          </button>
            {questionError && (
            <p className="question-error">
              {questionError}
            </p>
          )}
        </div>

      </div>
    </div>
  );
}

export default App;