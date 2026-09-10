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
  const [agentProcess, setAgentProcess] = useState([]);
  const [openAgentProcess, setOpenAgentProcess] = useState(null);

  const fileInputRef = useRef(null);

  const formatScore = (score) => {
    if (score === "" || score === null || score === undefined) {
      return "N/A";
    }

    const number = Number(score);

    if (Number.isNaN(number)) {
      return "N/A";
    }

    return `${number.toFixed(1)}/1.0`;
  };

  // Ask a question
  const askQuestion = async () => {
    if (!question.trim()) {
      setQuestionError("Please enter a question");
      return;
    }

    if (documents.length === 0) {
      setQuestionError("Please upload a research paper first.");
      return;
    }

    if (loading) {
      return;
    }

    const currentQuestion = question.trim();
    let currentProcess = [];

    setLoading(true);
    setQuestionError("");
    setUploadMessage("");
    setAgentProcess([]);

    try {
      const response = await fetch(
        "http://localhost:8000/ask-stream",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question: currentQuestion,
          }),
        }
      );

      if (!response.ok) {
        const errorText = await response.text();

        setQuestionError(
          errorText || "Failed to connect to the research agent."
        );

        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();

        if (done) {
          break;
        }

        buffer += decoder.decode(value, {
          stream: true,
        });

        const events = buffer.split("\n\n");

        buffer = events.pop() || "";

        for (const event of events) {
          if (!event.trim()) {
            continue;
          }

          let eventType = "";
          let eventData = "";

          const lines = event.split("\n");

          for (const line of lines) {
            if (line.startsWith("event:")) {
              eventType = line.slice(6).trim();
            }

            if (line.startsWith("data:")) {
              eventData += line.slice(5).trim();
            }
          }

          // Live Agent Process
          if (eventType === "step") {
            const step = JSON.parse(eventData);

            currentProcess.push(step);

            setAgentProcess([...currentProcess]);

            await new Promise((resolve) =>
              setTimeout(resolve, 10)
            );
          }

          // Final result
          if (eventType === "result") {
            const data = JSON.parse(eventData);

            setAnswer(data.answer || "");
            setSources(data.sources || "");
            setContextScore(data.context_score ?? "");
            setAnswerScore(data.answer_score ?? "");
            setFaithfulnessScore(
              data.faithfulness_score ?? ""
            );

            setChatHistory((previousHistory) => [
              ...previousHistory,
              {
                question: currentQuestion,
                answer: data.answer || "",
                sources: data.sources || "",
                contextScore: data.context_score ?? "",
                answerScore: data.answer_score ?? "",
                faithfulnessScore:
                  data.faithfulness_score ?? "",
                agentProcess: [...currentProcess],
              },
            ]);

            setQuestion("");
            setQuestionError("");
          }

          // Backend error
          if (eventType === "error") {
            const message = JSON.parse(eventData);

            currentProcess.push(`❌ ${message}`);

            setAgentProcess([...currentProcess]);

            setQuestionError(message);
          }
        }
      }
    } catch (error) {
      console.error(error);

      setQuestionError(
        error.message || "Unable to connect to the backend."
      );
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

    await new Promise((resolve) =>
      setTimeout(resolve, 500)
    );

    setUploadStatus("Processing PDF and building search index...");

    try {
      const response = await fetch(
        "http://localhost:8000/upload",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setUploadMessage(
          data.detail || "Upload failed."
        );

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

      setFile(null);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (error) {
      console.error(error);

      setUploadMessage(
        "Error connecting to the backend."
      );

      setUploadStatus("Upload failed.");
    } finally {
      setUploading(false);
    }
  };

  // Clear documents
  const clearDocuments = async () => {
    const confirmClear = window.confirm(
      "Are you sure you want to clear all documents and chat history?"
    );

    if (!confirmClear) {
      return;
    }

    try {
      const response = await fetch(
        "http://localhost:8000/clear",
        {
          method: "DELETE",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setUploadMessage(
          "Failed to clear documents."
        );

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
      setQuestionError("");

      setUploadStatus("");
      setAgentProcess([]);
      setFile(null);
      setOpenAgentProcess(null);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      setUploadMessage(
        data.message ||
          "Documents cleared successfully."
      );
    } catch (error) {
      console.error(error);

      setUploadMessage(
        "Error connecting to the backend."
      );
    }
  };

  return (
    <div className="app">
      <div className="container">

        {/* Header */}
        <header className="header">
          <h1>
            Agentic RAG Research Assistant
          </h1>

          <p>
            Ask questions about your research papers
            and get grounded answers with sources.
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
              const selectedFile =
                e.target.files[0];

              if (!selectedFile) {
                return;
              }

              if (
                selectedFile.type !==
                  "application/pdf" &&
                !selectedFile.name
                  .toLowerCase()
                  .endsWith(".pdf")
              ) {
                setFile(null);

                setUploadMessage(
                  "Please upload a PDF file."
                );

                if (fileInputRef.current) {
                  fileInputRef.current.value = "";
                }

                return;
              }

              setFile(selectedFile);
              setUploadMessage("");
              setUploadStatus("");
            }}
            disabled={uploading}
          />

          <button
            type="button"
            onClick={uploadPDF}
            disabled={uploading}
          >
            {uploading
              ? "Uploading..."
              : "Upload PDF"}
          </button>

          {uploadMessage && (
            <p className="upload-message">
              {uploadMessage}
            </p>
          )}

          {uploadStatus && (
            <div className="upload-status">
              {uploadStatus}
            </div>
          )}
        </div>

        {/* Documents Section */}
        <div className="documents-section">
          <div className="documents-header">

            <h2>Documents</h2>

            <button
              onClick={clearDocuments}
              disabled={
                documents.length === 0 ||
                uploading
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

              {documents.map(
                (document, index) => (
                  <div
                    className="document-item"
                    key={index}
                  >
                    ✓ {document}
                  </div>
                )
              )}

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

                    <p>
                      {chat.question}
                    </p>
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

                    <button
                      className="view-process-button"
                      onClick={() => {
                        setOpenAgentProcess(
                          openAgentProcess === index
                            ? null
                            : index
                        );
                      }}
                    >
                      {openAgentProcess === index
                        ? "Hide Agent Process ▲"
                        : "View Agent Process ▼"}
                    </button>

                    {openAgentProcess === index && (
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
                          <p>
                            No process information
                            available.
                          </p>
                        )}

                      </div>
                    )}

                  </div>

                  {/* Evaluation */}
                  <div className="info-card">

                    <h3>Evaluation</h3>

                    <div className="score">
                      <span>
                        Context Relevance
                      </span>

                      <strong>
                        {formatScore(
                          chat.contextScore
                        )}
                      </strong>
                    </div>

                    <div className="score">
                      <span>
                        Answer Relevance
                      </span>

                      <strong>
                        {formatScore(
                          chat.answerScore
                        )}
                      </strong>
                    </div>

                    <div className="score">
                      <span>
                        Faithfulness
                      </span>

                      <strong>
                        {formatScore(
                          chat.faithfulnessScore
                        )}
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
                                {source.replace(
                                  /^-\s*/,
                                  ""
                                )}
                              </p>
                            )
                          )
                      ) : (
                        <p>
                          No sources available.
                        </p>
                      )}

                    </div>

                  </div>

                </aside>

              </div>
            ))}

          </div>
        )}

        {/* Live Agent Process */}
        {loading && (
          <div className="info-card">

            <h3>Agent Process</h3>

            <div className="agent-process">

              {agentProcess.length === 0 ? (
                <div className="process-step">
                  Starting agent...
                </div>
              ) : (
                agentProcess.map(
                  (step, index) => (
                    <div
                      className="process-step"
                      key={index}
                    >
                      {step}
                    </div>
                  )
                )
              )}

            </div>

          </div>
        )}

        {/* Question Section */}
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
              documents.length === 0 ||
              loading
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
            {loading
              ? "Searching..."
              : "Ask"}
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