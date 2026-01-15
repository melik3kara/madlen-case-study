import { useState, useRef, useEffect } from 'react';
import { ChevronDown, Check, Cpu, Image, Zap, Search, Loader2 } from 'lucide-react';
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
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  const selectedModelInfo = models.find((m) => m.id === selectedModel);

  // Filter models by search query
  const filteredModels = models.filter((model) =>
    model.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    model.id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSearchQuery('');
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Focus search input when dropdown opens
  useEffect(() => {
    if (isOpen && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isOpen]);

  const handleSelect = (modelId: string) => {
    onSelectModel(modelId);
    setIsOpen(false);
    setSearchQuery('');
  };

  const getProviderColor = (modelId: string): string => {
    if (modelId.includes('google')) return 'from-blue-500 to-green-500';
    if (modelId.includes('meta') || modelId.includes('llama')) return 'from-blue-600 to-indigo-600';
    if (modelId.includes('mistral')) return 'from-orange-500 to-red-500';
    if (modelId.includes('openai')) return 'from-emerald-500 to-teal-500';
    if (modelId.includes('deepseek')) return 'from-purple-500 to-pink-500';
    if (modelId.includes('qwen')) return 'from-cyan-500 to-blue-500';
    if (modelId.includes('nvidia')) return 'from-green-500 to-lime-500';
    if (modelId.includes('xiaomi')) return 'from-orange-400 to-amber-500';
    return 'from-primary-500 to-secondary-500';
  };

  return (
    <div ref={dropdownRef} className="relative">
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={isLoading}
        className={`w-full flex items-center justify-between gap-3 px-4 py-3 rounded-xl border-2 transition-all duration-200 ${
          isOpen 
            ? 'border-primary-500 bg-white dark:bg-dark-800 ring-4 ring-primary-500/20' 
            : 'border-dark-200 dark:border-dark-700 bg-white dark:bg-dark-800 hover:border-primary-400'
        } ${isLoading ? 'opacity-70 cursor-not-allowed' : 'cursor-pointer'}`}
      >
        {isLoading ? (
          <div className="flex items-center gap-3">
            <Loader2 className="w-5 h-5 animate-spin text-primary-500" />
            <span className="text-dark-500 dark:text-dark-400">Modeller yükleniyor...</span>
          </div>
        ) : selectedModelInfo ? (
          <div className="flex items-center gap-3 min-w-0">
            <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${getProviderColor(selectedModelInfo.id)} flex items-center justify-center flex-shrink-0`}>
              <Cpu className="w-4 h-4 text-white" />
            </div>
            <div className="text-left min-w-0">
              <p className="text-sm font-medium text-dark-900 dark:text-dark-100 truncate">
                {selectedModelInfo.name}
              </p>
              <div className="flex items-center gap-2 text-xs text-dark-500 dark:text-dark-400">
                {selectedModelInfo.supports_images && (
                  <span className="flex items-center gap-1 text-secondary-600 dark:text-secondary-400">
                    <Image className="w-3 h-3" />
                    Multimodal
                  </span>
                )}
                <span className="flex items-center gap-1">
                  <Zap className="w-3 h-3 text-primary-500" />
                  Ücretsiz
                </span>
              </div>
            </div>
          </div>
        ) : (
          <span className="text-dark-500 dark:text-dark-400">Model seçin</span>
        )}
        
        <ChevronDown 
          className={`w-5 h-5 text-dark-400 transition-transform duration-200 flex-shrink-0 ${
            isOpen ? 'rotate-180' : ''
          }`} 
        />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-white dark:bg-dark-800 rounded-2xl shadow-2xl border border-dark-200 dark:border-dark-700 overflow-hidden z-50 animate-fade-in">
          {/* Search Input */}
          <div className="p-3 border-b border-dark-200 dark:border-dark-700">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-400" />
              <input
                ref={searchInputRef}
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Model ara..."
                className="w-full pl-10 pr-4 py-2 rounded-xl bg-dark-50 dark:bg-dark-900 border border-dark-200 dark:border-dark-700 text-sm focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all"
              />
            </div>
          </div>

          {/* Models List */}
          <div className="max-h-80 overflow-y-auto">
            {filteredModels.length === 0 ? (
              <div className="p-4 text-center text-dark-500 dark:text-dark-400 text-sm">
                Model bulunamadı
              </div>
            ) : (
              <div className="p-2">
                {filteredModels.map((model) => (
                  <button
                    key={model.id}
                    onClick={() => handleSelect(model.id)}
                    className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all duration-150 ${
                      model.id === selectedModel
                        ? 'bg-gradient-to-r from-primary-50 to-secondary-50 dark:from-primary-900/30 dark:to-secondary-900/30'
                        : 'hover:bg-dark-50 dark:hover:bg-dark-700/50'
                    }`}
                  >
                    {/* Provider Icon */}
                    <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${getProviderColor(model.id)} flex items-center justify-center flex-shrink-0`}>
                      <Cpu className="w-5 h-5 text-white" />
                    </div>

                    {/* Model Info */}
                    <div className="flex-1 text-left min-w-0">
                      <p className={`text-sm font-medium truncate ${
                        model.id === selectedModel
                          ? 'text-primary-700 dark:text-primary-300'
                          : 'text-dark-900 dark:text-dark-100'
                      }`}>
                        {model.name}
                      </p>
                      <div className="flex items-center gap-2 mt-0.5">
                        {model.context_length && (
                          <span className="text-xs text-dark-500 dark:text-dark-400">
                            {Math.round(model.context_length / 1000)}K context
                          </span>
                        )}
                        {model.supports_images && (
                          <span className="flex items-center gap-1 text-xs text-secondary-600 dark:text-secondary-400">
                            <Image className="w-3 h-3" />
                            Vision
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Selected Check */}
                    {model.id === selectedModel && (
                      <div className="w-6 h-6 rounded-full bg-primary-500 flex items-center justify-center flex-shrink-0">
                        <Check className="w-4 h-4 text-white" />
                      </div>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="p-3 border-t border-dark-200 dark:border-dark-700 bg-dark-50 dark:bg-dark-900/50">
            <p className="text-xs text-center text-dark-500 dark:text-dark-400">
              {filteredModels.length} ücretsiz model mevcut
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
