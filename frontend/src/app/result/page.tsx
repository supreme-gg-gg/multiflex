"use client";

import { useState, useEffect } from "react";
import Card from "../../components/Card";
import Hero from "../../components/Hero";
import Gallery from "../../components/Gallery";
import List from "../../components/List";
import Stats from "../../components/Stats";
import Testimonial from "../../components/Testimonial";

interface ComponentProps {
  type: string;
  props: any;
}

export default function Result() {
  const [loading, setLoading] = useState(true);
  const [components, setComponents] = useState<ComponentProps[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const prompt = localStorage.getItem("userPrompt");
    if (prompt) {
      fetch("http://localhost:8000/api/agent", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt }),
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
      setError("No prompt found");
      setLoading(false);
    }
  }, []);

  const renderComponent = (comp: ComponentProps, index: number) => {
    switch (comp.type) {
      case "card":
        return <Card key={index} {...comp.props} />;
      case "hero":
        return <Hero key={index} {...comp.props} />;
      case "gallery":
        return <Gallery key={index} {...comp.props} />;
      case "list":
        return <List key={index} {...comp.props} />;
      case "stats":
        return <Stats key={index} {...comp.props} />;
      case "testimonial":
        return <Testimonial key={index} {...comp.props} />;
      default:
        return (
          <div key={index} className="card p-6">
            <div className="flex items-start space-x-3">
              <div className="w-2 h-16 bg-gradient-to-b from-red-400 to-orange-500 rounded-full"></div>
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-gray-800 mb-3">
                  🚧 Unknown Component
                </h2>
                <p className="text-gray-600 text-lg">
                  Component type "{comp.type}" is not supported yet, but we're
                  working on it!
                </p>
              </div>
            </div>
          </div>
        );
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center animate-fade-in">
          <div className="relative">
            <div className="w-20 h-20 border-4 border-white/30 border-t-white rounded-full animate-spin mx-auto mb-6"></div>
            <div
              className="absolute inset-0 w-20 h-20 border-4 border-transparent border-t-purple-400 rounded-full animate-spin mx-auto"
              style={{
                animationDirection: "reverse",
                animationDuration: "1.5s",
              }}
            ></div>
          </div>
          <h1 className="text-2xl font-semibold text-white mb-2">
            🎨 Creating your UI...
          </h1>
          <p className="text-white/70">Our AI is working its magic</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="w-full max-w-md animate-fade-in">
          <div className="card p-8 text-center">
            <div className="text-6xl mb-4">😅</div>
            <h1 className="text-xl font-bold text-red-600 mb-4">Oops!</h1>
            <p className="text-gray-700 mb-6">{error}</p>
            <button
              onClick={() => (window.location.href = "/")}
              className="btn-primary text-white py-3 px-6 rounded-xl font-medium w-full animate-pulse-hover"
            >
              🔄 Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-4">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8 animate-fade-in">
          <button
            onClick={() => (window.location.href = "/")}
            className="glass text-white py-3 px-6 rounded-xl font-medium hover:bg-white/30 transition-all duration-200 mb-4"
          >
            ← Back to Home
          </button>
          <h1 className="text-3xl font-bold text-white mb-2">
            ✨ Your Generated UI
          </h1>
          <p className="text-white/80">Here's what our AI created for you</p>
        </div>

        {components && components.length > 0 ? (
          <div className="space-y-6 animate-fade-in">
            {components.map((comp, index) => renderComponent(comp, index))}
          </div>
        ) : (
          <div className="card p-8 text-center animate-fade-in">
            <div className="text-6xl mb-4">🤔</div>
            <h2 className="text-xl font-bold text-gray-800 mb-2">
              No components generated
            </h2>
            <p className="text-gray-600">
              The AI didn't return any components. Try a different prompt!
            </p>
          </div>
        )}

        <div className="mt-8 text-center">
          <button
            onClick={() => (window.location.href = "/")}
            className="btn-primary text-white py-3 px-8 rounded-xl font-medium animate-pulse-hover"
          >
            🎨 Create Another
          </button>
        </div>
      </div>
    </div>
  );
}
