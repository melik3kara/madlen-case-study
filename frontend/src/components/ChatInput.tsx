import { useState, useRef, ChangeEvent } from 'react';
import { Send, Loader2, Image, X } from 'lucide-react';
import type { ImageData } from '../types';

interface ChatInputProps {
  onSendMessage: (message: string, image?: ImageData) => void;
  isLoading: boolean;
  disabled?: boolean;
  supportsImages?: boolean;
}

export function ChatInput({
  onSendMessage,
  isLoading,
  disabled = false,
  supportsImages = false,
}: ChatInputProps) {
  const [message, setMessage] = useState('');
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [imageData, setImageData] = useState<ImageData | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading && !disabled) {
      onSendMessage(message.trim(), imageData || undefined);
      setMessage('');
      setImagePreview(null);
      setImageData(null);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleImageSelect = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = (reader.result as string).split(',')[1];
        setImageData({
          base64_data: base64,
          media_type: file.type,
        });
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const removeImage = () => {
    setImagePreview(null);
    setImageData(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t bg-white p-4">
      {/* Image Preview */}
      {imagePreview && (
        <div className="mb-3 relative inline-block">
          <img
            src={imagePreview}
            alt="Preview"
            className="h-20 w-20 object-cover rounded-lg border"
          />
          <button
            type="button"
            onClick={removeImage}
            className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 transition-colors"
          >
            <X size={14} />
          </button>
        </div>
      )}

      <div className="flex items-end gap-3">
        {/* Image Upload Button */}
        {supportsImages && (
          <>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleImageSelect}
              accept="image/*"
              className="hidden"
            />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={isLoading || disabled}
              className="p-3 rounded-lg border border-gray-300 text-gray-600 hover:bg-gray-50 hover:border-gray-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="Resim ekle"
            >
              <Image size={20} />
            </button>
          </>
        )}

        {/* Message Input */}
        <div className="flex-1 relative">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Mesajınızı yazın... (Shift+Enter ile yeni satır)"
            disabled={isLoading || disabled}
            rows={1}
            className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            style={{ minHeight: '48px', maxHeight: '120px' }}
          />
        </div>

        {/* Send Button */}
        <button
          type="submit"
          disabled={!message.trim() || isLoading || disabled}
          className="p-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center"
        >
          {isLoading ? (
            <Loader2 size={20} className="animate-spin" />
          ) : (
            <Send size={20} />
          )}
        </button>
      </div>

      {/* Character count */}
      <div className="mt-2 text-xs text-gray-500 text-right">
        {message.length} karakter
      </div>
    </form>
  );
}
