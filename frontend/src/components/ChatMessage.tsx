import { User, Bot, Copy, Check, Image as ImageIcon } from 'lucide-react';
import { useState } from 'react';
import type { ChatMessage as ChatMessageType } from '../types';

interface ChatMessageProps {
  message: ChatMessageType;
  isLatest?: boolean;
}

export function ChatMessage({ message, isLatest = false }: ChatMessageProps) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formatTime = (timestamp?: string) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('tr-TR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div 
      className={`group flex gap-4 p-5 rounded-2xl transition-all duration-200 ${
        isLatest ? 'animate-slide-up' : ''
      } ${
        isUser 
          ? 'bg-gradient-to-r from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20 ml-8' 
          : 'bg-white dark:bg-dark-800 shadow-sm border border-dark-100 dark:border-dark-700 mr-8'
      }`}
    >
      {/* Avatar */}
      <div className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center shadow-md ${
        isUser
          ? 'bg-gradient-to-br from-primary-500 to-secondary-500'
          : 'bg-gradient-to-br from-dark-700 to-dark-900 dark:from-dark-600 dark:to-dark-800'
      }`}>
        {isUser ? (
          <User className="w-5 h-5 text-white" />
        ) : (
          <Bot className="w-5 h-5 text-white" />
        )}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        {/* Header */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className={`text-sm font-semibold ${
              isUser 
                ? 'text-primary-700 dark:text-primary-400' 
                : 'text-dark-700 dark:text-dark-200'
            }`}>
              {isUser ? 'Siz' : 'AI Asistan'}
            </span>
            {message.timestamp && (
              <span className="text-xs text-dark-400 dark:text-dark-500">
                {formatTime(message.timestamp)}
              </span>
            )}
          </div>

          {/* Copy button */}
          {!isUser && (
            <button
              onClick={handleCopy}
              className="opacity-0 group-hover:opacity-100 p-2 rounded-lg hover:bg-dark-100 dark:hover:bg-dark-700 transition-all duration-200"
              title="Kopyala"
            >
              {copied ? (
                <Check className="w-4 h-4 text-green-500" />
              ) : (
                <Copy className="w-4 h-4 text-dark-400" />
              )}
            </button>
          )}
        </div>

        {/* Image preview if exists */}
        {message.image && (
          <div className="mb-3 inline-block">
            <div className="relative group/image">
              <img
                src={`data:${message.image.media_type};base64,${message.image.base64_data}`}
                alt="Uploaded"
                className="max-w-xs max-h-48 rounded-xl border-2 border-primary-200 dark:border-primary-800 shadow-md"
              />
              <div className="absolute bottom-2 left-2 px-2 py-1 bg-dark-900/70 backdrop-blur-sm rounded-lg flex items-center gap-1">
                <ImageIcon className="w-3 h-3 text-white" />
                <span className="text-xs text-white">Görsel</span>
              </div>
            </div>
          </div>
        )}

        {/* Message content */}
        <div className={`message-content text-sm leading-relaxed ${
          isUser 
            ? 'text-dark-800 dark:text-dark-200' 
            : 'text-dark-700 dark:text-dark-300'
        }`}>
          {message.content.split('\n').map((line, i) => (
            <p key={i} className={line === '' ? 'h-3' : ''}>
              {line}
            </p>
          ))}
        </div>

        {/* Model info for AI messages */}
        {!isUser && message.model && (
          <div className="mt-3 flex items-center gap-2">
            <span className="text-xs px-2 py-1 rounded-lg bg-dark-100 dark:bg-dark-700 text-dark-500 dark:text-dark-400">
              {message.model.split('/').pop()?.replace(':free', '')}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
