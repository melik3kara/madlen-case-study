import { useState, useEffect, useCallback } from 'react';
import { Header, MessageList, ChatInput, ErrorMessage, Sidebar } from './components';
import type { ChatSession } from './components';
import { chatApi, modelsApi, ApiException } from './services';
import type { ChatMessage, ModelInfo, ImageData } from './types';
import { Trash2, PlusCircle } from 'lucide-react';

function App() {
  // Theme state
  const [isDark, setIsDark] = useState(() => {
    const saved = localStorage.getItem('theme');
    return saved ? saved === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  // Sidebar state
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [sessions, setSessions] = useState<ChatSession[]>([]);

  // Chat state
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingModels, setIsLoadingModels] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Apply theme to document
  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDark);
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
  }, [isDark]);

  // Load models and history on mount
  useEffect(() => {
    loadModels();
    loadHistory();
  }, []);

  // Load sessions when messages change
  useEffect(() => {
    loadSessions();
  }, [messages]);

  const loadModels = async () => {
    setIsLoadingModels(true);
    try {
      const response = await modelsApi.getModels();
      setModels(response.models);
      if (response.models.length > 0 && !selectedModel) {
        // Try to find a good default model
        const preferredModels = [
          'meta-llama/llama-3.3-70b-instruct:free',
          'google/gemma-3-27b-it:free',
          'xiaomi/mimo-v2-flash:free',
        ];
        const defaultModel = preferredModels.find(id => 
          response.models.some(m => m.id === id)
        ) || response.models[0].id;
        setSelectedModel(defaultModel);
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
    }
  };

  const loadSessions = async () => {
    try {
      const response = await chatApi.getSessions();
      const mappedSessions: ChatSession[] = response.sessions.map(s => ({
        id: s.id,
        title: s.title,
        messageCount: s.message_count,
        lastUpdated: s.last_updated,
        isActive: s.is_active,
      }));
      setSessions(mappedSessions);
    } catch (err) {
      console.error('Failed to load sessions:', err);
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
        image,
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
      // Reload sessions to update the sidebar
      await loadSessions();
    } catch (err) {
      console.error('Failed to create new session:', err);
      setError('Yeni oturum oluşturulurken hata oluştu.');
    }
  };

  const handleSelectSession = async (id: string) => {
    try {
      const response = await chatApi.switchSession(id);
      if (response.success) {
        // Map messages to ChatMessage format
        const mappedMessages: ChatMessage[] = response.messages.map(msg => ({
          role: msg.role as 'user' | 'assistant' | 'system',
          content: msg.content,
          timestamp: msg.timestamp,
          model: msg.model,
        }));
        setMessages(mappedMessages);
        setError(null);
        // Reload sessions to update active state
        await loadSessions();
      }
    } catch (err) {
      console.error('Failed to switch session:', err);
      setError('Oturum değiştirilirken hata oluştu.');
    }
  };

  const handleDeleteSession = async (id: string) => {
    try {
      await chatApi.deleteSession(id);
      // If we deleted the active session, clear messages
      const deletedSession = sessions.find(s => s.id === id);
      if (deletedSession?.isActive) {
        setMessages([]);
      }
      // Reload sessions
      await loadSessions();
    } catch (err) {
      console.error('Failed to delete session:', err);
      setError('Oturum silinirken hata oluştu.');
    }
  };

  const handleDismissError = () => {
    setError(null);
  };

  const handleRetry = () => {
    setError(null);
  };

  // Check if selected model supports images
  const selectedModelInfo = models.find((m) => m.id === selectedModel);
  const supportsImages = selectedModelInfo?.supports_images ?? false;

  return (
    <div className={`h-screen flex flex-col ${isDark ? 'dark' : ''}`}>
      {/* Header */}
      <Header
        models={models}
        selectedModel={selectedModel}
        onSelectModel={setSelectedModel}
        isLoadingModels={isLoadingModels}
        isDark={isDark}
        onToggleTheme={() => setIsDark(!isDark)}
      />

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <Sidebar
          sessions={sessions}
          onNewSession={handleNewSession}
          onSelectSession={handleSelectSession}
          onDeleteSession={handleDeleteSession}
          currentMessageCount={messages.length}
          isCollapsed={isSidebarCollapsed}
          onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        />

        {/* Chat Area */}
        <main className="flex-1 flex flex-col min-w-0">
          {/* Action bar */}
          <div className="flex items-center justify-between px-6 py-3 border-b border-dark-200/50 dark:border-dark-700/50 bg-white/50 dark:bg-dark-900/50 backdrop-blur-xl">
            <div className="flex items-center gap-2">
              <span className="text-sm text-dark-500 dark:text-dark-400">
                {messages.length > 0 ? `${messages.length} mesaj` : 'Yeni sohbet'}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={handleNewSession}
                className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium rounded-lg bg-dark-100 dark:bg-dark-800 text-dark-700 dark:text-dark-300 hover:bg-dark-200 dark:hover:bg-dark-700 transition-colors"
              >
                <PlusCircle className="w-4 h-4" />
                <span className="hidden sm:inline">Yeni Sohbet</span>
              </button>
              <button
                onClick={handleClearChat}
                disabled={messages.length === 0}
                className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium rounded-lg bg-accent-50 dark:bg-accent-900/20 text-accent-600 dark:text-accent-400 hover:bg-accent-100 dark:hover:bg-accent-900/30 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Trash2 className="w-4 h-4" />
                <span className="hidden sm:inline">Temizle</span>
              </button>
            </div>
          </div>

          {/* Error message */}
          {error && (
            <ErrorMessage
              message={error}
              onRetry={handleRetry}
              onDismiss={handleDismissError}
            />
          )}

          {/* Messages */}
          <MessageList messages={messages} isLoading={isLoading} />

          {/* Input */}
          <ChatInput
            onSend={handleSendMessage}
            isLoading={isLoading}
            supportsImages={supportsImages}
            placeholder={selectedModelInfo ? `${selectedModelInfo.name} ile sohbet et...` : 'Mesajınızı yazın...'}
          />
        </main>
      </div>
    </div>
  );
}

export default App;
