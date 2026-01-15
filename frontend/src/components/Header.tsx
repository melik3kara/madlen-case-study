import { ExternalLink, Cpu, Sparkles, Activity, GraduationCap } from 'lucide-react';
import { ModelSelector } from './ModelSelector';
import { ThemeToggle } from './ThemeToggle';
import type { ModelInfo } from '../types';

interface HeaderProps {
  models: ModelInfo[];
  selectedModel: string;
  onSelectModel: (modelId: string) => void;
  isLoadingModels: boolean;
  isDark: boolean;
  onToggleTheme: () => void;
}

export function Header({
  models,
  selectedModel,
  onSelectModel,
  isLoadingModels,
  isDark,
  onToggleTheme,
}: HeaderProps) {
  const selectedModelInfo = models.find(m => m.id === selectedModel);

  return (
    <header className="relative z-20">
      {/* Main header */}
      <div className="glass-strong border-b border-dark-200/50 dark:border-dark-700/50">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between gap-6">
            {/* Logo & Brand */}
            <div className="flex items-center gap-4">
              {/* Logo with gradient background */}
              <div className="relative">
                <div className="w-12 h-12 bg-gradient-to-br from-primary-500 via-secondary-500 to-accent-500 rounded-2xl flex items-center justify-center text-white shadow-lg transform hover:scale-105 transition-transform duration-200">
                  <GraduationCap className="w-7 h-7" />
                </div>
                {/* Glow effect */}
                <div className="absolute inset-0 bg-gradient-to-br from-primary-500 via-secondary-500 to-accent-500 rounded-2xl blur-xl opacity-30 -z-10" />
              </div>
              
              <div>
                <h1 className="text-xl font-bold">
                  <span className="gradient-text">MADLEN</span>
                  <span className="text-dark-700 dark:text-dark-300 ml-2 font-medium">AI Chat</span>
                </h1>
                <p className="text-xs text-dark-500 dark:text-dark-400 flex items-center gap-1.5">
                  <Sparkles className="w-3 h-3 text-primary-500" />
                  Great Teachers Great Futures!
                </p>
              </div>
            </div>

            {/* Model Selector - Center */}
            <div className="flex-1 max-w-md">
              <ModelSelector
                models={models}
                selectedModel={selectedModel}
                onSelectModel={onSelectModel}
                isLoading={isLoadingModels}
              />
            </div>

            {/* Right Actions */}
            <div className="flex items-center gap-3">
              {/* Model info badge */}
              {selectedModelInfo && (
                <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-dark-100 dark:bg-dark-800 border border-dark-200 dark:border-dark-700">
                  <Cpu className="w-4 h-4 text-primary-500" />
                  <span className="text-xs text-dark-600 dark:text-dark-400">
                    {selectedModelInfo.context_length 
                      ? `${Math.round(selectedModelInfo.context_length / 1000)}K context`
                      : 'AI Model'
                    }
                  </span>
                </div>
              )}

              {/* Theme Toggle */}
              <ThemeToggle isDark={isDark} onToggle={onToggleTheme} />

              {/* Jaeger Link */}
              <a
                href="http://localhost:16686"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-dark-100 dark:bg-dark-800 hover:bg-dark-200 dark:hover:bg-dark-700 border border-dark-200 dark:border-dark-700 text-dark-700 dark:text-dark-300 transition-all duration-200 group"
                title="Jaeger Tracing UI'ı Aç"
              >
                <Activity className="w-4 h-4 text-secondary-500 group-hover:animate-pulse" />
                <span className="text-sm font-medium hidden sm:inline">Traces</span>
                <ExternalLink className="w-3 h-3 opacity-50" />
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Decorative gradient line */}
      <div className="h-1 bg-gradient-to-r from-primary-500 via-secondary-500 to-accent-500 opacity-80" />
    </header>
  );
}
