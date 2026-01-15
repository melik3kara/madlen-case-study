import { useRef, useEffect } from 'react';
import { MessageSquare } from 'lucide-react';
import { ChatMessage } from './ChatMessage';
import { TypingIndicator } from './TypingIndicator';
import type { ChatMessage as ChatMessageType } from '../types';

interface MessageListProps {
  messages: ChatMessageType[];
  isLoading: boolean;
}

export function MessageList({ messages, isLoading }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  if (messages.length === 0 && !isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-center text-gray-500">
          <MessageSquare size={48} className="mx-auto mb-4 text-gray-300" />
          <h3 className="text-lg font-medium text-gray-700 mb-2">
            Sohbete Başlayın
          </h3>
          <p className="text-sm max-w-sm">
            AI modellerinden biriyle sohbet etmeye başlamak için aşağıdaki
            alana mesajınızı yazın.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="divide-y divide-gray-100">
        {messages.map((message, index) => (
          <ChatMessage key={`${message.timestamp}-${index}`} message={message} />
        ))}
        {isLoading && <TypingIndicator />}
      </div>
      <div ref={messagesEndRef} />
    </div>
  );
}
