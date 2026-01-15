import { useState, useEffect, useCallback } from 'react';
import { Header, MessageList, ChatInput, ErrorMessage } from './components';
import { chatApi, modelsApi, ApiException } from './services';
import type { ChatMessage, ModelInfo, ImageData } from './types';

function App() {
  // State
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingModels, setIsLoadingModels] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load models on mount
  useEffect(() => {
    loadModels();
    loadHistory();
  }, []);

  const loadModels = async () => {
    setIsLoadingModels(true);
    try {
      const response = await modelsApi.getModels();
      setModels(response.models);
      if (response.models.length > 0 && !selectedModel) {
        setSelectedModel(response.models[0].id);
      }
    } catch (err) {
      console.error('Failed to load models:', err);
      setError('Modeller yüklenirken hata oluştu. Lütfen sayfayı yenileyin.');
    } finally {
      setIsLoadingModels(false);
    }
  };

  const loadHistory = async () => {
    try {
      const response = await chatApi.getHistory();
      setMessages(response.messages);
    } catch (err) {
      console.error('Failed to load history:', err);
      // Don't show error for history load failure on initial load
    }
  };

  const handleSendMessage = useCallback(
    async (content: string, image?: ImageData) => {
      if (!content.trim() || isLoading) return;

      setError(null);
      setIsLoading(true);

      // Optimistically add user message
      const userMessage: ChatMessage = {
        role: 'user',
        content,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);

      try {
        const response = await chatApi.sendMessage({
          message: content,
          model: selectedModel,
          image,
        });

        if (response.success) {
          setMessages((prev) => [...prev, response.message]);
        } else {
          throw new Error(response.error || 'Mesaj gönderilemedi');
        }
      } catch (err) {
        console.error('Failed to send message:', err);
        // Remove the optimistically added user message
        setMessages((prev) => prev.slice(0, -1));

        if (err instanceof ApiException) {
          setError(err.detail || err.message);
        } else if (err instanceof Error) {
          setError(err.message);
        } else {
          setError('Mesaj gönderilirken beklenmeyen bir hata oluştu.');
        }
      } finally {
        setIsLoading(false);
      }
    },
    [selectedModel, isLoading]
  );

  const handleClearChat = async () => {
    try {
      await chatApi.clearHistory();
      setMessages([]);
      setError(null);
    } catch (err) {
      console.error('Failed to clear chat:', err);
      setError('Sohbet temizlenirken hata oluştu.');
    }
  };

  const handleNewSession = async () => {
    try {
      await chatApi.newSession();
      setMessages([]);
      setError(null);
    } catch (err) {
      console.error('Failed to create new session:', err);
      setError('Yeni oturum oluşturulurken hata oluştu.');
    }
  };

  const handleDismissError = () => {
    setError(null);
  };

  const handleRetry = () => {
    setError(null);
    // If there's a failed message, we could retry it
    // For now, just clear the error
  };

  // Check if selected model supports images
  const selectedModelInfo = models.find((m) => m.id === selectedModel);
  const supportsImages = selectedModelInfo?.supports_images ?? false;

  return (
    <div className="h-screen flex flex-col bg-gray-100">
      <Header
        models={models}
        selectedModel={selectedModel}
        onSelectModel={setSelectedModel}
        onClearChat={handleClearChat}
        onNewSession={handleNewSession}
        isLoadingModels={isLoadingModels}
        messageCount={messages.length}
      />

      <main className="flex-1 flex flex-col max-w-5xl w-full mx-auto bg-white shadow-xl overflow-hidden">
        {error && (
          <ErrorMessage
            message={error}
            onRetry={handleRetry}
            onDismiss={handleDismissError}
          />
        )}

        <MessageList messages={messages} isLoading={isLoading} />

        <ChatInput
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          disabled={isLoadingModels || !selectedModel}
          supportsImages={supportsImages}
        />
      </main>

      {/* Footer */}
      <footer className="text-center py-2 text-xs text-gray-500">
        <p>
          OpenRouter API ile güçlendirilmiştir • OpenTelemetry ile izleniyor •{' '}
          <a
            href="http://localhost:16686"
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary-600 hover:underline"
          >
            Jaeger UI
          </a>
        </p>
      </footer>
    </div>
  );
}

export default App;
