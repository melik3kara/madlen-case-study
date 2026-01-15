import { Bot } from 'lucide-react';

export function TypingIndicator() {
  return (
    <div className="flex gap-4 p-5 rounded-2xl bg-white dark:bg-dark-800 shadow-sm border border-dark-100 dark:border-dark-700 mr-8 animate-fade-in">
      {/* Avatar */}
      <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br from-dark-700 to-dark-900 dark:from-dark-600 dark:to-dark-800 flex items-center justify-center shadow-md">
        <Bot className="w-5 h-5 text-white" />
      </div>

      {/* Typing animation */}
      <div className="flex items-center gap-3 py-2">
        <div className="flex items-center gap-1.5">
          <div className="typing-dot" />
          <div className="typing-dot" />
          <div className="typing-dot" />
        </div>
        <span className="text-sm text-dark-500 dark:text-dark-400">
          AI düşünüyor...
        </span>
      </div>
    </div>
  );
}
