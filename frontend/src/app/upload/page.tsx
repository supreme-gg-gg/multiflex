"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Upload() {
  const [files, setFiles] = useState<FileList | null>(null);
  const [userId, setUserId] = useState("demo-user");
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const router = useRouter();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFiles(e.target.files);
  };

  const handleUpload = async () => {
    if (!files || files.length === 0) return;

    setUploading(true);
    setResults(null);

    try {
      const formData = new FormData();
      for (let i = 0; i < files.length; i++) {
        formData.append("files", files[i]);
      }
      formData.append("user_id", userId);

      const response = await fetch("http://localhost:8000/api/upload", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      setResults(result);
    } catch (error) {
      console.error("Upload error:", error);
      setResults({ error: "Upload failed" });
    } finally {
      setUploading(false);
    }
  };

  const supportedTypes = [".pdf", ".docx", ".pptx", ".txt"];

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-4">
            📚 Upload Educational Materials
          </h1>
          <p className="text-white/80 text-lg">
            Upload your study materials to enhance AI responses
          </p>
        </div>

        <div className="card p-8 space-y-6">
          {/* User ID Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              User ID
            </label>
            <input
              type="text"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-400 focus:outline-none"
              placeholder="Enter your user ID"
            />
          </div>

          {/* File Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Educational Documents
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-purple-400 transition-colors">
              <input
                type="file"
                multiple
                accept=".pdf,.docx,.pptx,.txt"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
              />
              <label htmlFor="file-upload" className="cursor-pointer">
                <div className="text-gray-600">
                  <svg
                    className="mx-auto h-12 w-12 text-gray-400 mb-4"
                    stroke="currentColor"
                    fill="none"
                    viewBox="0 0 48 48"
                  >
                    <path
                      d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                  <p className="text-lg">Click to upload files</p>
                  <p className="text-sm text-gray-500 mt-2">
                    Supported: {supportedTypes.join(", ")}
                  </p>
                  <p className="text-sm text-gray-500">Max 10MB per file</p>
                </div>
              </label>
            </div>

            {files && (
              <div className="mt-4">
                <p className="text-sm text-gray-600 mb-2">Selected files:</p>
                <ul className="text-sm space-y-1">
                  {Array.from(files).map((file, index) => (
                    <li key={index} className="flex justify-between">
                      <span>{file.name}</span>
                      <span className="text-gray-500">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            disabled={!files || uploading}
            className="w-full btn-primary text-white py-3 px-6 rounded-xl font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? (
              <span className="flex items-center justify-center">
                <svg
                  className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                Uploading...
              </span>
            ) : (
              "📚 Upload Documents"
            )}
          </button>

          {/* Results */}
          {results && (
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="font-medium text-gray-900 mb-2">Upload Results</h3>
              {results.error ? (
                <p className="text-red-600">{results.error}</p>
              ) : (
                <div className="space-y-2">
                  <p className="text-green-600">{results.message}</p>
                  <p className="text-sm text-gray-600">
                    Total chunks created: {results.total_chunks}
                  </p>
                  {results.results && (
                    <div className="space-y-1">
                      {results.results.map((result: any, index: number) => (
                        <div
                          key={index}
                          className={`text-sm p-2 rounded ${
                            result.status === "success"
                              ? "bg-green-100 text-green-800"
                              : "bg-red-100 text-red-800"
                          }`}
                        >
                          <strong>{result.filename}:</strong> {result.message}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Navigation */}
          <div className="flex gap-4">
            <button
              onClick={() => router.push("/")}
              className="flex-1 py-2 px-4 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              ← Back to Chat
            </button>
            <button
              onClick={() => router.push(`/manage?user=${userId}`)}
              className="flex-1 py-2 px-4 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200"
            >
              Manage Documents →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
