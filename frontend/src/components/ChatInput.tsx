import { useState, useRef, useCallback, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { ImageUpload } from './ImageUpload';
import type { ImageData } from '../types';

interface ChatInputProps {
  onSend: (message: string, image?: ImageData) => void;
  isLoading: boolean;
  supportsImages: boolean;
  placeholder?: string;
}

export function ChatInput({ 
  onSend, 
  isLoading, 
  supportsImages,
  placeholder = "Mesajınızı yazın..." 
}: ChatInputProps) {
  const [message, setMessage] = useState('');
  const [selectedImage, setSelectedImage] = useState<ImageData | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  const adjustHeight = useCallback(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
    }
  }, []);

  useEffect(() => {
    adjustHeight();
  }, [message, adjustHeight]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSend(message.trim(), selectedImage || undefined);
      setMessage('');
      setSelectedImage(null);
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="border-t border-dark-200 dark:border-dark-700 bg-white/80 dark:bg-dark-900/80 backdrop-blur-xl p-4">
      <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
        {/* Selected image preview */}
        {selectedImage && (
          <div className="mb-3 flex items-center gap-3 px-4 py-3 rounded-xl bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800 animate-fade-in">
            <img
              src={`data:${selectedImage.media_type};base64,${selectedImage.base64_data}`}
              alt="Preview"
              className="w-16 h-16 rounded-lg object-cover border-2 border-primary-300 dark:border-primary-700"
            />
            <div className="flex-1">
              <p className="text-sm font-medium text-primary-700 dark:text-primary-300">
                Görsel eklendi
              </p>
              <p className="text-xs text-primary-600 dark:text-primary-400">
                Mesajınızla birlikte gönderilecek
              </p>
            </div>
          </div>
        )}

        <div className="flex items-end gap-3">
          {/* Image Upload Button */}
          <ImageUpload
            onImageSelect={setSelectedImage}
            selectedImage={selectedImage}
            disabled={isLoading}
            supportsImages={supportsImages}
          />

          {/* Text Input */}
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              disabled={isLoading}
              rows={1}
              className="w-full px-5 py-3.5 rounded-2xl border-2 border-dark-200 dark:border-dark-700 bg-white dark:bg-dark-800 text-dark-900 dark:text-dark-100 placeholder:text-dark-400 dark:placeholder:text-dark-500 focus:border-primary-500 dark:focus:border-primary-400 focus:ring-4 focus:ring-primary-500/20 outline-none transition-all duration-200 resize-none disabled:opacity-60 disabled:cursor-not-allowed pr-14"
              style={{ minHeight: '52px' }}
            />
            
            {/* Character count */}
            {message.length > 100 && (
              <span className="absolute right-14 bottom-3.5 text-xs text-dark-400 dark:text-dark-500">
                {message.length}
              </span>
            )}
          </div>

          {/* Send Button */}
          <button
            type="submit"
            disabled={!message.trim() || isLoading}
            className={`flex-shrink-0 w-12 h-12 rounded-xl flex items-center justify-center transition-all duration-200 ${
              message.trim() && !isLoading
                ? 'bg-gradient-to-r from-primary-500 via-secondary-500 to-accent-500 text-white shadow-lg hover:shadow-xl transform hover:-translate-y-0.5'
                : 'bg-dark-100 dark:bg-dark-800 text-dark-400 dark:text-dark-500 cursor-not-allowed'
            }`}
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>

        {/* Helper text */}
        <div className="mt-2 flex items-center justify-between px-1">
          <p className="text-xs text-dark-400 dark:text-dark-500">
            Enter ile gönder, Shift+Enter ile satır atla
          </p>
          {supportsImages && (
            <p className="text-xs text-secondary-500 dark:text-secondary-400">
              📸 Bu model görsel destekliyor
            </p>
          )}
        </div>
      </form>
    </div>
  );
}
