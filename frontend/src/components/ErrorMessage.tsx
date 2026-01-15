import { AlertCircle, RefreshCw, X } from 'lucide-react';

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
  onDismiss?: () => void;
}

export function ErrorMessage({ message, onRetry, onDismiss }: ErrorMessageProps) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 m-4">
      <div className="flex items-start gap-3">
        <AlertCircle className="text-red-500 flex-shrink-0 mt-0.5" size={20} />
        <div className="flex-1">
          <h4 className="text-sm font-medium text-red-800 mb-1">
            Bir hata oluştu
          </h4>
          <p className="text-sm text-red-700">{message}</p>
          <div className="mt-3 flex gap-2">
            {onRetry && (
              <button
                onClick={onRetry}
                className="inline-flex items-center gap-1 text-sm font-medium text-red-700 hover:text-red-800"
              >
                <RefreshCw size={14} />
                Tekrar Dene
              </button>
            )}
          </div>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="text-red-400 hover:text-red-600 transition-colors"
          >
            <X size={18} />
          </button>
        )}
      </div>
    </div>
  );
}
