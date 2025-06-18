/**
 * API configuration for MultiFlex frontend
 */

// hardcoded for now to avoid issues with .env.local
export const API_BASE_URL =
  "https://ui-agent-backend-106594148836.us-central1.run.app";

export const API_ENDPOINTS = {
  agent: `${API_BASE_URL}/api/agent`,
  upload: `${API_BASE_URL}/api/upload`,
  documents: (userId: string) => `${API_BASE_URL}/api/documents/${userId}`,
  testRag: `${API_BASE_URL}/api/test-rag`,
} as const;
