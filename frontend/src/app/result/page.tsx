"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import ChatInterface from "../../components/ChatInterface";

export default function Result() {
  const router = useRouter();
  const [userPrompt, setUserPrompt] = useState("");
  const [htmlContent, setHtmlContent] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [connected, setConnected] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
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
            ws.current.send(
              JSON.stringify({
                prompt,
                user_id: "anonymous",
              })
            );
          } else {
            console.log("Reconnected - not sending initial prompt again");
          }
        };

        ws.current.onmessage = (event) => {
          console.log("Received message from agent");
          setProcessing(false);

          try {
            const response = JSON.parse(event.data);
            console.log("Parsed response:", response);

            if (response.type === "html_update") {
              setHtmlContent(response.html_content);
              if (response.session_id) {
                setSessionId(response.session_id);
              }
              setLoading(false);
              setConnected(true);
            } else if (response.type === "error") {
              setError(response.message || "Unknown error occurred");
              setLoading(false);
            }
          } catch (parseError) {
            // Fallback for plain text responses (legacy support)
            console.log("Received plain text response, treating as HTML");
            setHtmlContent(event.data);
            setLoading(false);
            setConnected(true);
          }
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

  // Send chat message handler
  const handleSendMessage = (message: string) => {
    if (!ws.current || ws.current.readyState !== WebSocket.OPEN) {
      console.error("WebSocket not available for sending message");
      return;
    }

    setProcessing(true);

    const payload = {
      type: "chat_message",
      message: message,
      session_id: sessionId,
      user_id: "anonymous",
    };

    console.log("Sending chat message:", payload);
    ws.current.send(JSON.stringify(payload));
  };

  // Legacy interaction handler (simplified)
  useEffect(() => {
    if (contentRef.current && htmlContent) {
      const handleClick = (event: Event) => {
        const target = event.target as HTMLElement;

        // Only handle clicks on elements with IDs
        if (target.id && ws.current?.readyState === WebSocket.OPEN) {
          const payload = {
            type: "interaction",
            action: "click",
            element_id: target.id,
            element_type: target.tagName.toLowerCase(),
          };

          console.log("Sending interaction:", payload);
          ws.current.send(JSON.stringify(payload));
        }
      };

      contentRef.current.addEventListener("click", handleClick, false);

      return () => {
        if (contentRef.current) {
          contentRef.current.removeEventListener("click", handleClick, false);
        }
      };
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
              className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg border transition-colors text-sm font-medium"
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

      {/* Main Content Area */}
      <main
        className="flex-1 bg-white"
        style={{ height: "calc(100vh - 76px)" }}
      >
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
              <p className="mt-4 text-gray-600">Generating your HTML page...</p>
            </div>
          </div>
        )}
      </main>

      {/* Floating Chat Interface */}
      {htmlContent && (
        <ChatInterface
          onSendMessage={handleSendMessage}
          isConnected={connected}
          isProcessing={processing}
        />
      )}
    </div>
  );
}
