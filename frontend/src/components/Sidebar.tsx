import { useState } from 'react';
import { 
  MessageSquare, 
  Plus, 
  Trash2, 
  ChevronLeft, 
  ChevronRight,
  Clock,
  Sparkles
} from 'lucide-react';

export interface ChatSession {
  id: string;
  title: string;
  messageCount: number;
  lastUpdated: string;
  isActive: boolean;
}

interface SidebarProps {
  sessions: ChatSession[];
  onNewSession: () => void;
  onSelectSession: (id: string) => void;
  onDeleteSession: (id: string) => void;
  currentMessageCount: number;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export function Sidebar({
  sessions,
  onNewSession,
  onSelectSession,
  onDeleteSession,
  currentMessageCount,
  isCollapsed,
  onToggleCollapse,
}: SidebarProps) {
  const [hoveredSession, setHoveredSession] = useState<string | null>(null);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Şimdi';
    if (diffMins < 60) return `${diffMins} dk önce`;
    if (diffHours < 24) return `${diffHours} saat önce`;
    if (diffDays < 7) return `${diffDays} gün önce`;
    return date.toLocaleDateString('tr-TR');
  };

  return (
    <aside 
      className={`relative h-full flex flex-col bg-white/50 dark:bg-dark-900/50 backdrop-blur-xl border-r border-dark-200/50 dark:border-dark-700/50 transition-all duration-300 ${
        isCollapsed ? 'w-16' : 'w-72'
      }`}
    >
      {/* Header */}
      <div className={`p-4 border-b border-dark-200/50 dark:border-dark-700/50 ${isCollapsed ? 'px-3' : ''}`}>
        {isCollapsed ? (
          <button
            onClick={onNewSession}
            className="w-full p-2 rounded-xl bg-gradient-to-r from-primary-500 via-secondary-500 to-accent-500 text-white shadow-lg hover:shadow-xl transition-all duration-200"
            title="Yeni Sohbet"
          >
            <Plus className="w-5 h-5 mx-auto" />
          </button>
        ) : (
          <button
            onClick={onNewSession}
            className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-gradient-to-r from-primary-500 via-secondary-500 to-accent-500 text-white font-medium shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200"
          >
            <Plus className="w-5 h-5" />
            <span>Yeni Sohbet</span>
          </button>
        )}
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto p-2">
        {!isCollapsed && (
          <div className="px-2 py-1.5 mb-2">
            <span className="text-xs font-medium text-dark-500 dark:text-dark-400 uppercase tracking-wider">
              Sohbet Geçmişi
            </span>
          </div>
        )}

        <div className="space-y-1">
          {sessions.map((session) => (
            <div
              key={session.id}
              onMouseEnter={() => setHoveredSession(session.id)}
              onMouseLeave={() => setHoveredSession(null)}
              onClick={() => onSelectSession(session.id)}
              className={`group relative rounded-xl cursor-pointer transition-all duration-200 ${
                session.isActive
                  ? 'bg-gradient-to-r from-primary-100 to-secondary-100 dark:from-primary-900/30 dark:to-secondary-900/30 shadow-md'
                  : 'hover:bg-dark-100 dark:hover:bg-dark-800'
              } ${isCollapsed ? 'p-2' : 'p-3'}`}
            >
              {isCollapsed ? (
                <div className="flex items-center justify-center">
                  <MessageSquare 
                    className={`w-5 h-5 ${
                      session.isActive 
                        ? 'text-primary-600 dark:text-primary-400' 
                        : 'text-dark-400 dark:text-dark-500'
                    }`} 
                  />
                </div>
              ) : (
                <>
                  <div className="flex items-start gap-3">
                    <div className={`p-1.5 rounded-lg ${
                      session.isActive 
                        ? 'bg-primary-500/20 dark:bg-primary-500/30' 
                        : 'bg-dark-100 dark:bg-dark-700'
                    }`}>
                      <MessageSquare 
                        className={`w-4 h-4 ${
                          session.isActive 
                            ? 'text-primary-600 dark:text-primary-400' 
                            : 'text-dark-400 dark:text-dark-500'
                        }`} 
                      />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className={`text-sm font-medium truncate ${
                        session.isActive 
                          ? 'text-dark-900 dark:text-dark-100' 
                          : 'text-dark-700 dark:text-dark-300'
                      }`}>
                        {session.title}
                      </h4>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs text-dark-500 dark:text-dark-400 flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {formatDate(session.lastUpdated)}
                        </span>
                        <span className="text-xs text-dark-400 dark:text-dark-500">
                          • {session.messageCount} mesaj
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Delete button */}
                  {hoveredSession === session.id && !session.isActive && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onDeleteSession(session.id);
                      }}
                      className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-lg bg-accent-500/10 text-accent-500 hover:bg-accent-500/20 transition-colors duration-200"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </>
              )}

              {/* Active indicator */}
              {session.isActive && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-gradient-to-b from-primary-500 to-secondary-500 rounded-r-full" />
              )}
            </div>
          ))}

          {sessions.length === 0 && !isCollapsed && (
            <div className="text-center py-8 px-4">
              <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-gradient-to-r from-primary-100 to-secondary-100 dark:from-primary-900/30 dark:to-secondary-900/30 flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-primary-500" />
              </div>
              <p className="text-sm text-dark-500 dark:text-dark-400">
                Henüz sohbet yok
              </p>
              <p className="text-xs text-dark-400 dark:text-dark-500 mt-1">
                Yeni bir sohbet başlatın
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Current session info */}
      {!isCollapsed && currentMessageCount > 0 && (
        <div className="p-4 border-t border-dark-200/50 dark:border-dark-700/50">
          <div className="flex items-center gap-2 text-sm text-dark-500 dark:text-dark-400">
            <MessageSquare className="w-4 h-4" />
            <span>Mevcut sohbet: {currentMessageCount} mesaj</span>
          </div>
        </div>
      )}

      {/* Collapse toggle button */}
      <button
        onClick={onToggleCollapse}
        className="absolute -right-3 top-1/2 -translate-y-1/2 w-6 h-12 bg-white dark:bg-dark-800 border border-dark-200 dark:border-dark-700 rounded-full flex items-center justify-center shadow-md hover:shadow-lg transition-all duration-200 z-10"
      >
        {isCollapsed ? (
          <ChevronRight className="w-4 h-4 text-dark-500" />
        ) : (
          <ChevronLeft className="w-4 h-4 text-dark-500" />
        )}
      </button>
    </aside>
  );
}
