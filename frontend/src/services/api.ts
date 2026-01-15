/**
 * API Service for communicating with the backend
 */

import type {
  ChatRequest,
  ChatResponse,
  ModelsResponse,
  HistoryResponse,
  ApiError,
} from '../types';

const API_BASE_URL = '/api';

/**
 * Custom error class for API errors
 */
export class ApiException extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public detail?: string
  ) {
    super(message);
    this.name = 'ApiException';
  }
}

/**
 * Generic fetch wrapper with error handling
 */
async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
  };

  const response = await fetch(url, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  });

  if (!response.ok) {
    let errorMessage = 'An error occurred';
    try {
      const errorData: ApiError = await response.json();
      errorMessage = errorData.detail || errorMessage;
    } catch {
      errorMessage = response.statusText || errorMessage;
    }
    throw new ApiException(errorMessage, response.status, errorMessage);
  }

  return response.json();
}

/**
 * Chat API endpoints
 */
export const chatApi = {
  /**
   * Send a chat message
   */
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    return fetchApi<ChatResponse>('/chat', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  /**
   * Get chat history
   */
  getHistory: async (): Promise<HistoryResponse> => {
    return fetchApi<HistoryResponse>('/chat/history');
  },

  /**
   * Clear chat history
   */
  clearHistory: async (): Promise<{ message: string; success: boolean }> => {
    return fetchApi('/chat/clear', {
      method: 'POST',
    });
  },

  /**
   * Start a new session
   */
  newSession: async (): Promise<{ message: string; session_id: string; success: boolean }> => {
    return fetchApi('/chat/new-session', {
      method: 'POST',
    });
  },

  /**
   * Get all sessions
   */
  getSessions: async (): Promise<{ 
    sessions: Array<{
      id: string;
      title: string;
      message_count: number;
      last_updated: string;
      is_active: boolean;
    }>;
    count: number;
    current_session_id: string;
  }> => {
    return fetchApi('/chat/sessions');
  },

  /**
   * Switch to a session
   */
  switchSession: async (sessionId: string): Promise<{
    message: string;
    session_id: string;
    messages: Array<{
      role: string;
      content: string;
      timestamp?: string;
      model?: string;
    }>;
    success: boolean;
  }> => {
    return fetchApi(`/chat/sessions/${sessionId}/switch`, {
      method: 'POST',
    });
  },

  /**
   * Delete a session
   */
  deleteSession: async (sessionId: string): Promise<{ message: string; session_id: string; success: boolean }> => {
    return fetchApi(`/chat/sessions/${sessionId}`, {
      method: 'DELETE',
    });
  },
};

/**
 * Models API endpoints
 */
export const modelsApi = {
  /**
   * Get available models
   */
  getModels: async (): Promise<ModelsResponse> => {
    return fetchApi<ModelsResponse>('/models');
  },
};
