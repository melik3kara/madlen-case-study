import { AlertTriangle, RefreshCw, X } from 'lucide-react';

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
  onDismiss?: () => void;
}

export function ErrorMessage({ message, onRetry, onDismiss }: ErrorMessageProps) {
  return (
    <div className="mx-4 mt-4 animate-slide-up">
      <div className="flex items-start gap-4 p-4 rounded-2xl bg-accent-50 dark:bg-accent-900/20 border border-accent-200 dark:border-accent-800">
        {/* Icon */}
        <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-accent-100 dark:bg-accent-900/30 flex items-center justify-center">
          <AlertTriangle className="w-5 h-5 text-accent-600 dark:text-accent-400" />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-semibold text-accent-800 dark:text-accent-200 mb-1">
            Hata Oluştu
          </h4>
          <p className="text-sm text-accent-700 dark:text-accent-300 break-words">
            {message}
          </p>

          {/* Actions */}
          <div className="mt-3 flex items-center gap-2">
            {onRetry && (
              <button
                onClick={onRetry}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-accent-600 text-white hover:bg-accent-700 transition-colors"
              >
                <RefreshCw className="w-3 h-3" />
                Tekrar Dene
              </button>
            )}
            {onDismiss && (
              <button
                onClick={onDismiss}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg text-accent-700 dark:text-accent-300 hover:bg-accent-100 dark:hover:bg-accent-900/30 transition-colors"
              >
                Kapat
              </button>
            )}
          </div>
        </div>

        {/* Close button */}
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="flex-shrink-0 p-1 rounded-lg text-accent-500 hover:text-accent-700 hover:bg-accent-100 dark:hover:bg-accent-900/30 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
}
