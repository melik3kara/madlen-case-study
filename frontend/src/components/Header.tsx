import { Bot, Trash2, PlusCircle, ExternalLink } from 'lucide-react';
import { ModelSelector } from './ModelSelector';
import type { ModelInfo } from '../types';

interface HeaderProps {
  models: ModelInfo[];
  selectedModel: string;
  onSelectModel: (modelId: string) => void;
  onClearChat: () => void;
  onNewSession: () => void;
  isLoadingModels: boolean;
  messageCount: number;
}

export function Header({
  models,
  selectedModel,
  onSelectModel,
  onClearChat,
  onNewSession,
  isLoadingModels,
  messageCount,
}: HeaderProps) {
  return (
    <header className="bg-white border-b shadow-sm">
      <div className="max-w-5xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between gap-4">
          {/* Logo & Title */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center text-white shadow-lg">
              <Bot size={24} />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">AI Chat</h1>
              <p className="text-xs text-gray-500">
                OpenRouter ile Güçlendirilmiş
              </p>
            </div>
          </div>

          {/* Model Selector */}
          <div className="flex-1 max-w-xs">
            <ModelSelector
              models={models}
              selectedModel={selectedModel}
              onSelectModel={onSelectModel}
              isLoading={isLoadingModels}
            />
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2">
            <button
              onClick={onNewSession}
              className="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              title="Yeni Oturum"
            >
              <PlusCircle size={16} />
              <span className="hidden sm:inline">Yeni</span>
            </button>
            <button
              onClick={onClearChat}
              disabled={messageCount === 0}
              className="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium text-red-600 bg-red-50 rounded-lg hover:bg-red-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="Sohbeti Temizle"
            >
              <Trash2 size={16} />
              <span className="hidden sm:inline">Temizle</span>
            </button>
            <a
              href="http://localhost:16686"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium text-primary-600 bg-primary-50 rounded-lg hover:bg-primary-100 transition-colors"
              title="Jaeger UI'ı Aç"
            >
              <ExternalLink size={16} />
              <span className="hidden sm:inline">Jaeger</span>
            </a>
          </div>
        </div>
      </div>
    </header>
  );
}
