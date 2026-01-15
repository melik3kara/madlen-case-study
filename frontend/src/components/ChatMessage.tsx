import { User, Bot } from 'lucide-react';
import type { ChatMessage as ChatMessageType } from '../types';

interface ChatMessageProps {
  message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('tr-TR', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div
      className={`flex gap-3 p-4 ${
        isUser ? 'bg-gray-50' : 'bg-white'
      }`}
    >
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser
            ? 'bg-primary-600 text-white'
            : 'bg-emerald-600 text-white'
        }`}
      >
        {isUser ? <User size={18} /> : <Bot size={18} />}
      </div>

      {/* Message Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="font-medium text-gray-900">
            {isUser ? 'Siz' : 'AI Asistan'}
          </span>
          {isAssistant && message.model && (
            <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
              {message.model.split('/').pop()?.replace(':free', '')}
            </span>
          )}
          <span className="text-xs text-gray-400">
            {formatTimestamp(message.timestamp)}
          </span>
        </div>
        <div className="message-content text-gray-700 whitespace-pre-wrap">
          {message.content}
        </div>
      </div>
    </div>
  );
}
