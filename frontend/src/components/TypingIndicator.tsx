import { Bot } from 'lucide-react';

export function TypingIndicator() {
  return (
    <div className="flex gap-3 p-4 bg-white">
      {/* Avatar */}
      <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-emerald-600 text-white">
        <Bot size={18} />
      </div>

      {/* Typing Animation */}
      <div className="flex items-center">
        <div className="flex gap-1 px-4 py-3 bg-gray-100 rounded-lg">
          <span className="typing-dot w-2 h-2 bg-gray-400 rounded-full"></span>
          <span className="typing-dot w-2 h-2 bg-gray-400 rounded-full"></span>
          <span className="typing-dot w-2 h-2 bg-gray-400 rounded-full"></span>
        </div>
      </div>
    </div>
  );
}
