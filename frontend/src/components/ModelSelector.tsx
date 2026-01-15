import { ChevronDown, Loader2, Cpu } from 'lucide-react';
import type { ModelInfo } from '../types';

interface ModelSelectorProps {
  models: ModelInfo[];
  selectedModel: string;
  onSelectModel: (modelId: string) => void;
  isLoading: boolean;
}

export function ModelSelector({
  models,
  selectedModel,
  onSelectModel,
  isLoading,
}: ModelSelectorProps) {
  const selectedModelInfo = models.find((m) => m.id === selectedModel);

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-lg text-gray-600">
        <Loader2 size={16} className="animate-spin" />
        <span className="text-sm">Modeller yükleniyor...</span>
      </div>
    );
  }

  return (
    <div className="relative">
      <label className="block text-xs font-medium text-gray-500 mb-1">
        AI Model
      </label>
      <div className="relative">
        <select
          value={selectedModel}
          onChange={(e) => onSelectModel(e.target.value)}
          className="w-full appearance-none bg-white border border-gray-300 rounded-lg px-4 py-2 pr-10 text-sm font-medium text-gray-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent cursor-pointer hover:border-gray-400 transition-colors"
        >
          {models.map((model) => (
            <option key={model.id} value={model.id}>
              {model.name}
              {model.supports_images ? ' 🖼️' : ''}
            </option>
          ))}
        </select>
        <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
          <ChevronDown size={16} />
        </div>
      </div>

      {/* Model Info */}
      {selectedModelInfo && (
        <div className="mt-2 flex items-center gap-2 text-xs text-gray-500">
          <Cpu size={12} />
          <span>
            {selectedModelInfo.context_length
              ? `${(selectedModelInfo.context_length / 1000).toFixed(0)}K context`
              : 'Standard context'}
          </span>
          {selectedModelInfo.supports_images && (
            <span className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
              Görsel Destekli
            </span>
          )}
        </div>
      )}
    </div>
  );
}
