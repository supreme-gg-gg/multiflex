"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [userId, setUserId] = useState("demo-user");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const router = useRouter();

  // Reset submitting state when component mounts (user navigates back)
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
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-lg animate-fade-in">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-4">✨ UI Agent</h1>
          <p className="text-white/80 text-lg">
            Describe what you want and watch it come to life
          </p>
        </div>

        <div className="card p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label
                htmlFor="userId"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                User ID (for personalized responses)
              </label>
              <input
                id="userId"
                type="text"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                className="w-full px-4 py-2 border-0 rounded-xl bg-gray-50 focus:bg-white focus:ring-2 focus:ring-purple-400 focus:outline-none transition-all duration-200"
                placeholder="Enter your user ID"
                disabled={isSubmitting}
              />
            </div>

            <div>
              <label
                htmlFor="prompt"
                className="block text-sm font-medium text-gray-700 mb-3"
              >
                What would you like to create?
              </label>
              <textarea
                id="prompt"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                className="w-full px-4 py-3 border-0 rounded-xl bg-gray-50 focus:bg-white focus:ring-2 focus:ring-purple-400 focus:outline-none transition-all duration-200 resize-none"
                placeholder="e.g., Explain calculus concepts from my notes, or create a todo list..."
                rows={4}
                disabled={isSubmitting}
              />
            </div>

            <button
              type="submit"
              disabled={!prompt.trim() || isSubmitting}
              className="w-full btn-primary text-white py-4 px-6 rounded-xl font-medium text-lg disabled:opacity-50 disabled:cursor-not-allowed animate-pulse-hover"
            >
              {isSubmitting ? (
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
                  Creating magic...
                </span>
              ) : (
                "✨ Generate UI"
              )}
            </button>
          </form>
        </div>

        <div className="mt-6 space-y-4">
          <div className="flex gap-4">
            <button
              onClick={() => router.push("/upload")}
              className="flex-1 py-2 px-4 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors"
            >
              📚 Upload Documents
            </button>
            <button
              onClick={() => router.push(`/manage?user=${userId}`)}
              className="flex-1 py-2 px-4 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors"
            >
              📖 Manage Documents
            </button>
          </div>
          <div className="text-center">
            <p className="text-white/60 text-sm">
              Powered by AI with RAG • Made with ❤️
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
