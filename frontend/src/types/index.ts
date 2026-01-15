/**
 * Type definitions for the chat application
 */

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  model?: string;
}

export interface ModelInfo {
  id: string;
  name: string;
  description?: string;
  context_length?: number;
  supports_images: boolean;
  pricing?: Record<string, unknown>;
}

export interface ChatRequest {
  message: string;
  model: string;
  image?: ImageData;
}

export interface ImageData {
  base64_data: string;
  media_type: string;
}

export interface ChatResponse {
  message: ChatMessage;
  success: boolean;
  error?: string;
}

export interface ModelsResponse {
  models: ModelInfo[];
  count: number;
}

export interface HistoryResponse {
  messages: ChatMessage[];
  count: number;
  session_id: string;
}

export interface ApiError {
  detail: string;
}
