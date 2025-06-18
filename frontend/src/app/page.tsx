"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [userId, setUserId] = useState("demo-user");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const router = useRouter();

  // Reset submitting state when component mounts
  useEffect(() => {
    setIsSubmitting(false);
  }, []);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setIsSubmitting(true);

    // Store prompt and user_id in localStorage for the result page
    localStorage.setItem("userPrompt", prompt);
    localStorage.setItem("userId", userId);

    // Navigate to result page
    router.push("/result");
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-3 hover:opacity-80 transition-opacity"
              >
                <div className="w-8 h-8 bg-gray-900 rounded-lg flex items-center justify-center">
                  <svg
                    className="w-5 h-5 text-white"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 0C4.477 0 0 4.484 0 10.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0110 4.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.203 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.31.678.921.678 1.856 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0020 10.017C20 4.484 15.522 0 10 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
                <h1 className="text-xl font-semibold text-gray-900">
                  View us on GitHub
                </h1>
              </a>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => router.push("/upload")}
                className="btn-secondary text-sm"
              >
                📄 Upload Docs
              </button>
              <button
                onClick={() => router.push(`/manage?user=${userId}`)}
                className="btn-secondary text-sm"
              >
                📚 Manage
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="chat-container">
        <div className="min-h-[calc(100vh-80px)] flex flex-col">
          {/* Welcome Section */}
          <div className="flex-1 flex flex-col items-center justify-center py-12">
            <div className="text-center mb-8 animate-fade-in">
              <div className="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <span className="text-white text-2xl">✨</span>
              </div>
              <h2 className="text-3xl font-bold text-gray-900 mb-2">
                Welcome to MultiFlex
              </h2>
              <p className="text-gray-600 text-lg max-w-md">
                Yours for smarter learning: gather and present knowledge in
                creative, personalized UI
              </p>
            </div>

            {/* Example prompts */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-8 w-full max-w-2xl">
              {[
                "Show me a summary of the most important topics in quantum physics from my uploaded notes",
                "What are the key differences between supervised and unsupervised learning?",
                "Find all definitions of 'entropy' in my documents and display them in a table",
                "Search for practice problems on calculus and present them as interactive cards",
              ].map((example, index) => (
                <button
                  key={index}
                  onClick={() => setPrompt(example)}
                  className="p-3 text-left text-sm text-gray-700 bg-white border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>

          {/* Input Area */}
          <div className="pb-6">
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* User ID Input */}
              <div className="input-area p-3">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  User ID
                </label>
                <input
                  type="text"
                  value={userId}
                  onChange={(e) => setUserId(e.target.value)}
                  className="w-full border-0 resize-none bg-transparent placeholder-gray-500"
                  placeholder="Enter your user ID for personalized responses"
                  disabled={isSubmitting}
                />
              </div>

              {/* Main Input */}
              <div className="input-area p-4">
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  className="w-full border-0 resize-none bg-transparent placeholder-gray-500 text-gray-900"
                  placeholder="Ask a question and I'll answer it like never before..."
                  rows={3}
                  disabled={isSubmitting}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleSubmit(e as any);
                    }
                  }}
                />
                <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
                  <span className="text-xs text-gray-500">
                    Press Enter to send, Shift+Enter for new line
                  </span>
                  <button
                    type="submit"
                    disabled={!prompt.trim() || isSubmitting}
                    className="btn-primary px-4 py-2 text-sm"
                  >
                    {isSubmitting ? (
                      <span className="flex items-center">
                        <svg
                          className="animate-spin -ml-1 mr-2 h-4 w-4"
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
                        Creating...
                      </span>
                    ) : (
                      "Search and Create"
                    )}
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
}
