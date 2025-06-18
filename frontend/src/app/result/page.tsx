"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";

export default function Result() {
  const router = useRouter();
  const [userPrompt, setUserPrompt] = useState("");
  const [htmlContent, setHtmlContent] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [connected, setConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);
  const contentRef = useRef<HTMLDivElement | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const prompt = localStorage.getItem("userPrompt");
    if (prompt) {
      setUserPrompt(prompt);
    } else {
      router.push("/");
      return;
    }

    // Try to connect to WebSocket
    const connectWebSocket = () => {
      try {
        // Use the same base URL as the API but with ws protocol
        const baseUrl = "ws://localhost:8000";
        const wsUrl = `${baseUrl}/ws/agent`;

        console.log("Attempting to connect to:", wsUrl);

        // Close existing connection if any
        if (ws.current) {
          ws.current.close();
        }

        ws.current = new WebSocket(wsUrl);

        ws.current.onopen = () => {
          console.log("WebSocket connected successfully");
          setError(null);
          setConnected(true);

          // Only send initial prompt if we don't have HTML content yet
          if (
            !htmlContent &&
            ws.current &&
            ws.current.readyState === WebSocket.OPEN
          ) {
            console.log("Sending initial prompt:", prompt);
            ws.current.send(JSON.stringify({ prompt }));
          } else {
            console.log("Reconnected - not sending initial prompt again");
          }
        };

        ws.current.onmessage = (event) => {
          console.log("Received HTML from agent");
          setHtmlContent(event.data);
          setLoading(false);
          setConnected(true);
        };

        ws.current.onerror = (event) => {
          console.error("WebSocket error:", event);
          setConnected(false);
          if (!htmlContent) {
            setError(
              "Failed to connect to the real-time UI server. Please make sure the backend is running on localhost:8000"
            );
            setLoading(false);
          }
        };

        ws.current.onclose = (event) => {
          console.log("WebSocket connection closed:", event.code, event.reason);
          setConnected(false);

          // Only show error if this isn't a normal closure and we don't have content yet
          if (event.code !== 1000 && !htmlContent) {
            setError("WebSocket connection lost unexpectedly");
            setLoading(false);
          } else if (event.code !== 1000 && htmlContent) {
            // Try to reconnect if we have content (user is actively using the app)
            console.log("Attempting to reconnect in 2 seconds...");
            reconnectTimeoutRef.current = setTimeout(() => {
              connectWebSocket();
            }, 2000);
          }
        };
      } catch (err) {
        console.error("Failed to create WebSocket:", err);
        setError("Failed to establish WebSocket connection");
        setLoading(false);
      }
    };

    // Small delay to ensure component is mounted
    const timeoutId = setTimeout(() => {
      connectWebSocket();
    }, 100);

    return () => {
      clearTimeout(timeoutId);
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (ws.current) {
        if (ws.current.readyState === WebSocket.OPEN) {
          ws.current.close(1000, "Component unmounting");
        }
        ws.current = null;
      }
    };
  }, [router]);

  useEffect(() => {
    console.log("Event listener setup useEffect triggered");
    console.log("contentRef.current:", !!contentRef.current);
    console.log("htmlContent length:", htmlContent?.length || 0);

    if (contentRef.current && htmlContent) {
      console.log("🔧 Setting up event listeners on content container");

      // Generic handler for meaningful interactions
      const sendInteraction = (
        action: string,
        element: HTMLElement,
        value?: any
      ) => {
        console.log(
          `🚀 Attempting to send interaction - Action: ${action}, Element: ${element.tagName}, ID: ${element.id}`
        );

        if (!element.id) {
          console.warn("⚠️ Element has no ID, skipping interaction");
          return;
        }

        if (!ws.current) {
          console.error("❌ WebSocket not available");
          return;
        }

        if (ws.current.readyState !== WebSocket.OPEN) {
          console.error("❌ WebSocket not open, state:", ws.current.readyState);
          return;
        }

        try {
          const payload: any = {
            action,
            element_id: element.id,
            element_type: element.tagName.toLowerCase(),
          };

          if (value !== undefined) {
            payload.value = value;
          }

          console.log("📤 Sending WebSocket message:", payload);
          ws.current.send(JSON.stringify(payload));
          console.log("✅ Successfully sent interaction:", payload);
        } catch (error) {
          console.error("❌ Failed to send interaction:", error);
        }
      };

      // Universal event handler with extensive logging
      const handleAllEvents = (event: Event) => {
        const target = event.target as HTMLElement;
        console.log(`🎯 Event detected: ${event.type}`, {
          tag: target.tagName,
          id: target.id,
          className: target.className,
          type: (target as any).type,
          value: (target as any).value,
        });

        // Handle different event types
        if (event.type === "click") {
          console.log("🖱️ Processing click event");
          if (target.id) {
            sendInteraction("click", target);
          } else {
            console.warn("Clicked element has no ID:", target);
          }
        } else if (event.type === "change") {
          console.log("📝 Processing change event");
          if (target.id) {
            sendInteraction("change", target, (target as any).value);
          } else {
            console.warn("Changed element has no ID:", target);
          }
        } else if (event.type === "submit") {
          console.log("📤 Processing submit event");
          if (target.id) {
            sendInteraction("submit", target);
          } else {
            console.warn("Submitted form has no ID:", target);
          }
        }
      };

      // Add event listeners with logging
      console.log("➕ Adding event listeners to content container");

      // Use only one set of event listeners to avoid duplicates
      contentRef.current.addEventListener("click", handleAllEvents, false);
      contentRef.current.addEventListener("change", handleAllEvents, false);
      contentRef.current.addEventListener("submit", handleAllEvents, false);

      console.log("✅ Event listeners added successfully");

      return () => {
        console.log("🧹 Cleaning up event listeners");
        if (contentRef.current) {
          contentRef.current.removeEventListener(
            "click",
            handleAllEvents,
            false
          );
          contentRef.current.removeEventListener(
            "change",
            handleAllEvents,
            false
          );
          contentRef.current.removeEventListener(
            "submit",
            handleAllEvents,
            false
          );
        }
      };
    } else {
      console.log("⏭️ Skipping event listener setup:", {
        hasContentRef: !!contentRef.current,
        hasHtmlContent: !!htmlContent,
      });
    }
  }, [htmlContent]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Let the agent cook...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-xl font-semibold text-red-600">Error</h1>
          <p className="text-gray-600 mt-2">{error}</p>
          <button
            onClick={() => router.push("/")}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Go Back
          </button>
        </div>
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

      {/* Connection Status */}
      {htmlContent && !connected && (
        <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-2 text-xs">
          🔄 Reconnecting to server...
        </div>
      )}

      {/* Large Canvas Area - Let the agent cook here */}
      <main className="w-full h-[calc(100vh-60px)] bg-white">
        {htmlContent ? (
          <div
            ref={contentRef}
            className="w-full h-full"
            dangerouslySetInnerHTML={{ __html: htmlContent }}
            style={{
              overflow: "auto",
              width: "100%",
              height: "100%",
              border: "none",
              margin: 0,
              padding: 0,
            }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">
                Generating your real-time UI...
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
