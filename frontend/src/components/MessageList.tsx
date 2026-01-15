import { useRef, useEffect } from 'react';
import { ChatMessage } from './ChatMessage';
import { TypingIndicator } from './TypingIndicator';
import { MessageSquarePlus, Sparkles } from 'lucide-react';
import type { ChatMessage as ChatMessageType } from '../types';

interface MessageListProps {
  messages: ChatMessageType[];
  isLoading: boolean;
  isDark?: boolean;
  responseTimes?: Map<number, number>;
}

export function MessageList({ messages, isLoading, isDark = false, responseTimes }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  if (messages.length === 0 && !isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center max-w-md animate-fade-in">
          {/* Decorative icon */}
          <div className="relative mx-auto w-24 h-24 mb-6">
            <div className="absolute inset-0 bg-gradient-to-br from-primary-500 via-secondary-500 to-accent-500 rounded-3xl blur-2xl opacity-30" />
            <div className="relative w-24 h-24 bg-gradient-to-br from-primary-100 to-secondary-100 dark:from-primary-900/30 dark:to-secondary-900/30 rounded-3xl flex items-center justify-center border border-primary-200 dark:border-primary-800">
              <MessageSquarePlus className="w-12 h-12 text-primary-500" />
            </div>
            <div className="absolute -top-2 -right-2 w-8 h-8 bg-accent-500 rounded-full flex items-center justify-center animate-bounce-subtle">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
          </div>

          {/* Welcome text */}
          <h2 className="text-2xl font-bold text-dark-900 dark:text-dark-100 mb-3">
            Sohbete Hoş Geldiniz!
          </h2>
          <p className="text-dark-600 dark:text-dark-400 mb-6 leading-relaxed">
            26+ ücretsiz AI modeli ile sohbet edebilirsiniz. 
            Bir model seçin ve mesajınızı yazın.
          </p>

          {/* Feature highlights */}
          <div className="grid grid-cols-2 gap-3 text-left">
            <div className="p-3 rounded-xl bg-white dark:bg-dark-800 border border-dark-200 dark:border-dark-700">
              <div className="w-8 h-8 rounded-lg bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center mb-2">
                <span className="text-lg">🤖</span>
              </div>
              <h3 className="text-sm font-medium text-dark-900 dark:text-dark-100">Çoklu Model</h3>
              <p className="text-xs text-dark-500 dark:text-dark-400">GPT, Llama, Gemini ve daha fazlası</p>
            </div>
            <div className="p-3 rounded-xl bg-white dark:bg-dark-800 border border-dark-200 dark:border-dark-700">
              <div className="w-8 h-8 rounded-lg bg-secondary-100 dark:bg-secondary-900/30 flex items-center justify-center mb-2">
                <span className="text-lg">📸</span>
              </div>
              <h3 className="text-sm font-medium text-dark-900 dark:text-dark-100">Görsel Desteği</h3>
              <p className="text-xs text-dark-500 dark:text-dark-400">Resim yükleyerek soru sorun</p>
            </div>
            <div className="p-3 rounded-xl bg-white dark:bg-dark-800 border border-dark-200 dark:border-dark-700">
              <div className="w-8 h-8 rounded-lg bg-accent-100 dark:bg-accent-900/30 flex items-center justify-center mb-2">
                <span className="text-lg">📊</span>
              </div>
              <h3 className="text-sm font-medium text-dark-900 dark:text-dark-100">Trace İzleme</h3>
              <p className="text-xs text-dark-500 dark:text-dark-400">Jaeger ile performans takibi</p>
            </div>
            <div className="p-3 rounded-xl bg-white dark:bg-dark-800 border border-dark-200 dark:border-dark-700">
              <div className="w-8 h-8 rounded-lg bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center mb-2">
                <span className="text-lg">🌙</span>
              </div>
              <h3 className="text-sm font-medium text-dark-900 dark:text-dark-100">Karanlık Mod</h3>
              <p className="text-xs text-dark-500 dark:text-dark-400">Göz dostu arayüz seçenekleri</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-4">
      {messages.map((message, index) => (
        <ChatMessage 
          key={`${message.role}-${index}-${message.timestamp}`} 
          message={message}
          isLatest={index === messages.length - 1}
          isDark={isDark}
          responseTime={message.role === 'assistant' ? responseTimes?.get(index) : undefined}
        />
      ))}
      
      {isLoading && <TypingIndicator />}
      
      <div ref={messagesEndRef} />
    </div>
  );
}
