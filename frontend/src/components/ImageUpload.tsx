import { useState, useRef, useCallback } from 'react';
import { Image, X, Upload, AlertCircle } from 'lucide-react';
import type { ImageData } from '../types';

interface ImageUploadProps {
  onImageSelect: (image: ImageData | null) => void;
  selectedImage: ImageData | null;
  disabled?: boolean;
  supportsImages: boolean;
}

// Maximum dimensions for resizing
const MAX_WIDTH = 1024;
const MAX_HEIGHT = 1024;
const MAX_FILE_SIZE = 2 * 1024 * 1024; // 2MB after compression
const JPEG_QUALITY = 0.8;

/**
 * Compress and resize image to reduce file size
 */
function compressImage(file: File): Promise<{ base64: string; mediaType: string; originalSize: number; compressedSize: number }> {
  return new Promise((resolve, reject) => {
    const img = new window.Image();
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    img.onload = () => {
      let { width, height } = img;
      
      // Calculate new dimensions maintaining aspect ratio
      if (width > MAX_WIDTH || height > MAX_HEIGHT) {
        const ratio = Math.min(MAX_WIDTH / width, MAX_HEIGHT / height);
        width = Math.round(width * ratio);
        height = Math.round(height * ratio);
      }
      
      canvas.width = width;
      canvas.height = height;
      
      if (!ctx) {
        reject(new Error('Canvas context not available'));
        return;
      }
      
      // Draw and compress
      ctx.drawImage(img, 0, 0, width, height);
      
      // Convert to JPEG for better compression (unless it's a PNG with transparency)
      const outputType = file.type === 'image/png' ? 'image/png' : 'image/jpeg';
      const base64 = canvas.toDataURL(outputType, JPEG_QUALITY);
      const base64Data = base64.split(',')[1];
      
      // Calculate compressed size (base64 is ~33% larger than binary)
      const compressedSize = Math.round((base64Data.length * 3) / 4);
      
      resolve({
        base64: base64Data,
        mediaType: outputType,
        originalSize: file.size,
        compressedSize
      });
    };
    
    img.onerror = () => reject(new Error('Failed to load image'));
    img.src = URL.createObjectURL(file);
  });
}

/**
 * Format file size to human readable string
 */
function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function ImageUpload({ 
  onImageSelect, 
  selectedImage, 
  disabled = false,
  supportsImages 
}: ImageUploadProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const processFile = useCallback(async (file: File) => {
    setError(null);
    setIsProcessing(true);

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setError('Lütfen bir görsel dosyası seçin');
      setIsProcessing(false);
      return;
    }

    // Check original file size - warn if very large
    if (file.size > 20 * 1024 * 1024) {
      setError('Dosya çok büyük (max 20MB). Daha küçük bir görsel seçin.');
      setIsProcessing(false);
      return;
    }

    try {
      const result = await compressImage(file);
      
      // Check if compressed size is still too large
      if (result.compressedSize > MAX_FILE_SIZE) {
        setError(`Görsel sıkıştırıldıktan sonra hala çok büyük (${formatSize(result.compressedSize)}). Daha küçük çözünürlüklü bir görsel seçin.`);
        setIsProcessing(false);
        return;
      }
      
      onImageSelect({
        base64_data: result.base64,
        media_type: result.mediaType as 'image/jpeg' | 'image/png' | 'image/gif' | 'image/webp',
      });
      
      // Show compression info if significant
      if (result.originalSize > result.compressedSize * 1.5) {
        console.log(`Image compressed: ${formatSize(result.originalSize)} → ${formatSize(result.compressedSize)}`);
      }
    } catch (err) {
      setError('Görsel işlenirken hata oluştu');
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  }, [onImageSelect]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);

    if (disabled || !supportsImages) return;

    const file = e.dataTransfer.files[0];
    if (file) {
      processFile(file);
    }
  }, [disabled, supportsImages, processFile]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled && supportsImages) {
      setIsDragOver(true);
    }
  }, [disabled, supportsImages]);

  const handleDragLeave = useCallback(() => {
    setIsDragOver(false);
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      processFile(file);
    }
    // Reset input so same file can be selected again
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [processFile]);

  const handleRemoveImage = useCallback(() => {
    onImageSelect(null);
    setError(null);
  }, [onImageSelect]);

  const handleButtonClick = () => {
    if (!disabled && supportsImages) {
      fileInputRef.current?.click();
    }
  };

  // If model doesn't support images, show disabled state
  if (!supportsImages) {
    return (
      <div className="relative">
        <button
          type="button"
          disabled
          className="p-2.5 rounded-xl bg-dark-100 dark:bg-dark-800 text-dark-400 dark:text-dark-500 cursor-not-allowed opacity-50"
          title="Bu model görsel desteklemiyor"
        >
          <Image className="w-5 h-5" />
        </button>
      </div>
    );
  }

  return (
    <div className="relative">
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/gif,image/webp"
        onChange={handleFileSelect}
        className="hidden"
        disabled={disabled}
      />

      {/* Selected image preview */}
      {selectedImage ? (
        <div className="relative group">
          <div className="w-12 h-12 rounded-xl overflow-hidden border-2 border-primary-500 shadow-lg">
            <img
              src={`data:${selectedImage.media_type};base64,${selectedImage.base64_data}`}
              alt="Selected"
              className="w-full h-full object-cover"
            />
          </div>
          <button
            type="button"
            onClick={handleRemoveImage}
            className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-accent-500 text-white rounded-full flex items-center justify-center shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 hover:bg-accent-600"
          >
            <X className="w-3 h-3" />
          </button>
        </div>
      ) : isProcessing ? (
        <div className="p-2.5 rounded-xl bg-primary-100 dark:bg-primary-900/30">
          <div className="w-5 h-5 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          className={`relative ${isDragOver ? 'scale-110' : ''} transition-transform duration-200`}
        >
          <button
            type="button"
            onClick={handleButtonClick}
            disabled={disabled}
            className={`p-2.5 rounded-xl transition-all duration-200 ${
              isDragOver
                ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 ring-2 ring-primary-500'
                : 'bg-dark-100 dark:bg-dark-800 text-dark-500 dark:text-dark-400 hover:bg-dark-200 dark:hover:bg-dark-700 hover:text-primary-500'
            } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            title="Görsel yükle (sürükle & bırak da desteklenir)"
          >
            {isDragOver ? (
              <Upload className="w-5 h-5" />
            ) : (
              <Image className="w-5 h-5" />
            )}
          </button>

          {/* Drag overlay indicator */}
          {isDragOver && (
            <div className="absolute inset-0 rounded-xl border-2 border-dashed border-primary-500 bg-primary-500/10 pointer-events-none" />
          )}
        </div>
      )}

      {/* Error message */}
      {error && (
        <div className="absolute bottom-full left-0 mb-2 px-3 py-2 bg-accent-500 text-white text-xs rounded-lg shadow-lg flex items-center gap-2 whitespace-nowrap animate-fade-in">
          <AlertCircle className="w-3 h-3" />
          {error}
        </div>
      )}
    </div>
  );
}
