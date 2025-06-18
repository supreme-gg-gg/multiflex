"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Card from "../../components/Card";
import Hero from "../../components/Hero";
import Gallery from "../../components/Gallery";
import List from "../../components/List";
import Stats from "../../components/Stats";
import Testimonial from "../../components/Testimonial";
import { API_ENDPOINTS } from "../../lib/api";

interface ComponentProps {
  type: string;
  props: any;
}

export default function Result() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [components, setComponents] = useState<ComponentProps[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [userPrompt, setUserPrompt] = useState("");

  useEffect(() => {
    const prompt = localStorage.getItem("userPrompt");
    const userId = localStorage.getItem("userId") || "anonymous";

    if (prompt) {
      setUserPrompt(prompt);
      fetch(API_ENDPOINTS.agent, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt, user_id: userId }),
      })
        .then((res) => {
          if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
          }
          return res.json();
        })
        .then((data) => {
          setComponents(data.components);
          if (data.error) {
            setError(data.error);
          }
          setLoading(false);
        })
        .catch((err) => {
          console.error("Error:", err);
          setError(err.message);
          setLoading(false);
        });
    } else {
      router.push("/");
    }
  }, [router]);

  const renderComponent = (comp: ComponentProps, index: number) => {
    const { type, props } = comp;
    const key = `${type}-${index}`;

    switch (type) {
      case "card":
        return <Card key={key} {...props} />;
      case "hero":
        return <Hero key={key} {...props} />;
      case "gallery":
        return <Gallery key={key} {...props} />;
      case "list":
        return <List key={key} {...props} />;
      case "stats":
        return <Stats key={key} {...props} />;
      case "testimonial":
        return <Testimonial key={key} {...props} />;
      default:
        return (
          <div key={key} className="response-card">
            <p className="text-red-600">Unknown component type: {type}</p>
          </div>
        );
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="border-b border-gray-200 bg-white">
          <div className="max-w-4xl mx-auto px-4 py-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">MF</span>
              </div>
              <h1 className="text-xl font-semibold text-gray-900">MultiFlex</h1>
            </div>
          </div>
        </header>

        {/* Loading Content */}
        <main className="chat-container">
          <div className="py-6 space-y-4">
            {/* User Message */}
            <div className="flex justify-end">
              <div className="max-w-2xl bg-blue-600 text-white rounded-2xl rounded-tr-md px-4 py-3">
                <p>{userPrompt}</p>
              </div>
            </div>

            {/* Loading Response */}
            <div className="flex justify-start">
              <div className="max-w-2xl bg-white border border-gray-200 rounded-2xl rounded-tl-md px-4 py-3">
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"
                      style={{ animationDelay: "0.2s" }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"
                      style={{ animationDelay: "0.4s" }}
                    ></div>
                  </div>
                  <span className="text-gray-600 text-sm">
                    Creating your UI components...
                  </span>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="border-b border-gray-200 bg-white">
          <div className="max-w-4xl mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">MF</span>
                </div>
                <h1 className="text-xl font-semibold text-gray-900">
                  MultiFlex
                </h1>
              </div>
              <button
                onClick={() => router.push("/")}
                className="btn-secondary text-sm"
              >
                ← New Chat
              </button>
            </div>
          </div>
        </header>

        {/* Error Content */}
        <main className="chat-container">
          <div className="py-6 space-y-4">
            {/* User Message */}
            <div className="flex justify-end">
              <div className="max-w-2xl bg-blue-600 text-white rounded-2xl rounded-tr-md px-4 py-3">
                <p>{userPrompt}</p>
              </div>
            </div>

            {/* Error Response */}
            <div className="flex justify-start">
              <div className="max-w-2xl bg-red-50 border border-red-200 rounded-2xl rounded-tl-md px-4 py-3">
                <div className="flex items-start space-x-2">
                  <span className="text-red-600 text-sm">⚠️</span>
                  <div>
                    <p className="text-red-800 font-medium">
                      Something went wrong
                    </p>
                    <p className="text-red-600 text-sm mt-1">{error}</p>
                    <button
                      onClick={() => router.push("/")}
                      className="mt-3 btn-primary text-sm"
                    >
                      Try Again
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">MF</span>
              </div>
              <h1 className="text-xl font-semibold text-gray-900">MultiFlex</h1>
            </div>
            <button
              onClick={() => router.push("/")}
              className="btn-secondary text-sm"
            >
              ← New Chat
            </button>
          </div>
        </div>
      </header>

      {/* Generated UI Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="py-6">
          {/* AI Response */}
          <div className="flex justify-center">
            {" "}
            {/* Centering the content block */}
            <div className="w-full animate-slide-up">
              {" "}
              {/* Ensuring it takes full available width */}
              <div className="bg-white border border-gray-200 rounded-2xl p-4 sm:p-6 mb-6">
                {" "}
                {/* Added responsive padding and increased bottom margin */}
                <div className="flex items-center space-x-2 mb-3">
                  <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center">
                    <span className="text-white text-xs">✨</span>
                  </div>
                  <span className="text-gray-900 font-medium">
                    UI Components Generated
                  </span>
                </div>
                {components && components.length > 0 ? (
                  <div className="component-grid">
                    {components.map((comp, index) =>
                      renderComponent(comp, index)
                    )}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="text-gray-400 text-4xl mb-2">🤔</div>
                    <p className="text-gray-600">
                      No components were generated. Try a different prompt!
                    </p>
                  </div>
                )}
              </div>
              {/* Regenerate Button */}
              <div className="text-center">
                <button
                  onClick={() => router.push("/")}
                  className="btn-primary text-sm"
                >
                  Generate Another UI
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
