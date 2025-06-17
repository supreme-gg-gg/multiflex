"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";

export default function Manage() {
  const [userId, setUserId] = useState("demo-user");
  const [documents, setDocuments] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const userParam = searchParams.get("user");
    if (userParam) {
      setUserId(userParam);
    }
  }, [searchParams]);

  useEffect(() => {
    if (userId) {
      fetchDocuments();
    }
  }, [userId]);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/documents/${userId}`
      );
      const result = await response.json();
      setDocuments(result);
    } catch (error) {
      console.error("Error fetching documents:", error);
    } finally {
      setLoading(false);
    }
  };

  const clearDocuments = async () => {
    if (
      !confirm(
        "Are you sure you want to clear all documents? This action cannot be undone."
      )
    ) {
      return;
    }

    try {
      const response = await fetch(
        `http://localhost:8000/api/documents/${userId}`,
        {
          method: "DELETE",
        }
      );
      const result = await response.json();
      alert(result.message);
      fetchDocuments();
    } catch (error) {
      console.error("Error clearing documents:", error);
      alert("Failed to clear documents");
    }
  };

  const testRAG = async () => {
    const query = prompt("Enter a test query:");
    if (!query) return;

    try {
      const formData = new FormData();
      formData.append("query", query);
      formData.append("user_id", userId);

      const response = await fetch("http://localhost:8000/api/test-rag", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      alert(`RAG Test Results:
Query: ${result.query}
Should use RAG: ${result.rag_decision.use_rag}
Retrieved docs: ${result.retrieved_documents}
Context length: ${result.context_length}

Preview: ${result.context_preview || "No context"}`);
    } catch (error) {
      console.error("Error testing RAG:", error);
      alert("RAG test failed");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-4xl">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-4">
            📖 Document Management
          </h1>
          <p className="text-white/80 text-lg">
            Manage your uploaded educational materials
          </p>
        </div>

        <div className="card p-8 space-y-6">
          {/* User ID Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              User ID
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-400 focus:outline-none"
                placeholder="Enter user ID"
              />
              <button
                onClick={fetchDocuments}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
              >
                Refresh
              </button>
            </div>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div>
              <p className="text-gray-600 mt-2">Loading documents...</p>
            </div>
          )}

          {/* Document Statistics */}
          {documents && documents.statistics && (
            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Document Statistics
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {documents.statistics.total_documents || 0}
                  </div>
                  <div className="text-sm text-gray-600">Documents</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {documents.statistics.total_chunks || 0}
                  </div>
                  <div className="text-sm text-gray-600">Chunks</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {documents.statistics.file_count || 0}
                  </div>
                  <div className="text-sm text-gray-600">Files</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">
                    {documents.statistics.files
                      ? documents.statistics.files.length
                      : 0}
                  </div>
                  <div className="text-sm text-gray-600">Unique</div>
                </div>
              </div>

              {/* File List */}
              {documents.statistics.files &&
                documents.statistics.files.length > 0 && (
                  <div className="mt-6">
                    <h4 className="font-medium text-gray-900 mb-2">
                      Uploaded Files:
                    </h4>
                    <div className="space-y-1">
                      {documents.statistics.files.map(
                        (file: string, index: number) => (
                          <div
                            key={index}
                            className="flex items-center justify-between py-2 px-3 bg-white rounded border"
                          >
                            <span className="text-sm text-gray-700">
                              {file}
                            </span>
                            <span className="text-xs text-gray-500">📄</span>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                )}
            </div>
          )}

          {/* No Documents State */}
          {documents &&
            documents.statistics &&
            documents.statistics.total_documents === 0 && (
              <div className="text-center py-8 bg-gray-50 rounded-lg">
                <div className="text-6xl mb-4">📚</div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No Documents Found
                </h3>
                <p className="text-gray-600 mb-4">
                  Upload some educational materials to get started!
                </p>
                <button
                  onClick={() => router.push("/upload")}
                  className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                >
                  Upload Documents
                </button>
              </div>
            )}

          {/* Actions */}
          <div className="flex flex-wrap gap-4">
            <button
              onClick={() => router.push("/")}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              ← Back to Chat
            </button>
            <button
              onClick={() => router.push("/upload")}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
            >
              📚 Upload More
            </button>
            <button
              onClick={testRAG}
              disabled={
                !documents || documents.statistics?.total_documents === 0
              }
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              🧪 Test RAG
            </button>
            <button
              onClick={clearDocuments}
              disabled={
                !documents || documents.statistics?.total_documents === 0
              }
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              🗑️ Clear All
            </button>
          </div>

          {/* Instructions */}
          <div className="bg-blue-50 rounded-lg p-4">
            <h4 className="font-medium text-blue-900 mb-2">💡 How it works:</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Upload educational materials (PDF, DOCX, PPTX, TXT)</li>
              <li>• Documents are processed and stored as searchable chunks</li>
              <li>
                • When you ask educational questions, the AI will use your
                materials
              </li>
              <li>
                • The system automatically detects when to use your documents vs
                web search
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
