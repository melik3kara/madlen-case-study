import { User, Bot, Copy, Check, Image as ImageIcon, Clock } from 'lucide-react';
import { useState, useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark, oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import type { ChatMessage as ChatMessageType } from '../types';

interface ChatMessageProps {
  message: ChatMessageType;
  isLatest?: boolean;
  isDark?: boolean;
  responseTime?: number;
}

export function ChatMessage({ message, isLatest = false, isDark = false, responseTime }: ChatMessageProps) {
  const [copied, setCopied] = useState(false);
  const [copiedCode, setCopiedCode] = useState<string | null>(null);
  const isUser = message.role === 'user';

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleCopyCode = async (code: string) => {
    await navigator.clipboard.writeText(code);
    setCopiedCode(code);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const formatTime = (timestamp?: string) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('tr-TR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  // Memoize the markdown components to prevent re-renders
  const markdownComponents = useMemo(() => ({
    // Code blocks with syntax highlighting
    code({ node, inline, className, children, ...props }: any) {
      const match = /language-(\w+)/.exec(className || '');
      const codeString = String(children).replace(/\n$/, '');
      
      if (!inline && match) {
        return (
          <div className="relative group/code my-3">
            <div className="absolute top-2 right-2 flex items-center gap-2 z-10">
              <span className="text-xs text-dark-400 bg-dark-800/80 dark:bg-dark-900/80 px-2 py-1 rounded">
                {match[1]}
              </span>
              <button
                onClick={() => handleCopyCode(codeString)}
                className="p-1.5 rounded-lg bg-dark-700/80 hover:bg-dark-600 transition-colors"
                title="Kodu kopyala"
              >
                {copiedCode === codeString ? (
                  <Check className="w-3.5 h-3.5 text-green-400" />
                ) : (
                  <Copy className="w-3.5 h-3.5 text-dark-300" />
                )}
              </button>
            </div>
            <SyntaxHighlighter
              style={isDark ? oneDark : oneLight}
              language={match[1]}
              PreTag="div"
              customStyle={{
                margin: 0,
                borderRadius: '0.75rem',
                fontSize: '0.875rem',
                padding: '1rem',
                paddingTop: '2.5rem',
              }}
              {...props}
            >
              {codeString}
            </SyntaxHighlighter>
          </div>
        );
      }
      
      // Inline code
      return (
        <code 
          className="px-1.5 py-0.5 rounded bg-dark-100 dark:bg-dark-700 text-primary-600 dark:text-primary-400 text-sm font-mono"
          {...props}
        >
          {children}
        </code>
      );
    },
    // Paragraphs
    p({ children }: any) {
      return <p className="mb-3 last:mb-0">{children}</p>;
    },
    // Lists
    ul({ children }: any) {
      return <ul className="list-disc list-inside mb-3 space-y-1">{children}</ul>;
    },
    ol({ children }: any) {
      return <ol className="list-decimal list-inside mb-3 space-y-1">{children}</ol>;
    },
    li({ children }: any) {
      return <li className="text-dark-700 dark:text-dark-300">{children}</li>;
    },
    // Headings
    h1({ children }: any) {
      return <h1 className="text-xl font-bold mb-3 text-dark-900 dark:text-dark-100">{children}</h1>;
    },
    h2({ children }: any) {
      return <h2 className="text-lg font-bold mb-2 text-dark-900 dark:text-dark-100">{children}</h2>;
    },
    h3({ children }: any) {
      return <h3 className="text-base font-bold mb-2 text-dark-900 dark:text-dark-100">{children}</h3>;
    },
    // Blockquotes
    blockquote({ children }: any) {
      return (
        <blockquote className="border-l-4 border-primary-400 dark:border-primary-600 pl-4 my-3 italic text-dark-600 dark:text-dark-400">
          {children}
        </blockquote>
      );
    },
    // Links
    a({ href, children }: any) {
      return (
        <a 
          href={href} 
          target="_blank" 
          rel="noopener noreferrer"
          className="text-primary-600 dark:text-primary-400 hover:underline"
        >
          {children}
        </a>
      );
    },
    // Tables
    table({ children }: any) {
      return (
        <div className="overflow-x-auto my-3">
          <table className="min-w-full border-collapse border border-dark-200 dark:border-dark-700">
            {children}
          </table>
        </div>
      );
    },
    th({ children }: any) {
      return (
        <th className="border border-dark-200 dark:border-dark-700 px-3 py-2 bg-dark-100 dark:bg-dark-800 font-semibold text-left">
          {children}
        </th>
      );
    },
    td({ children }: any) {
      return (
        <td className="border border-dark-200 dark:border-dark-700 px-3 py-2">
          {children}
        </td>
      );
    },
    // Horizontal rule
    hr() {
      return <hr className="my-4 border-dark-200 dark:border-dark-700" />;
    },
    // Strong/Bold
    strong({ children }: any) {
      return <strong className="font-semibold text-dark-900 dark:text-dark-100">{children}</strong>;
    },
    // Emphasis/Italic
    em({ children }: any) {
      return <em className="italic">{children}</em>;
    },
  }), [isDark, copiedCode]);

  return (
    <div 
      className={`group flex gap-4 p-5 rounded-2xl transition-all duration-200 ${
        isLatest ? 'animate-slide-up' : ''
      } ${
        isUser 
          ? 'bg-gradient-to-r from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20 ml-8' 
          : 'bg-white dark:bg-dark-800 shadow-sm border border-dark-100 dark:border-dark-700 mr-8'
      }`}
    >
      {/* Avatar */}
      <div className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center shadow-md ${
        isUser
          ? 'bg-gradient-to-br from-primary-500 to-secondary-500'
          : 'bg-gradient-to-br from-dark-700 to-dark-900 dark:from-dark-600 dark:to-dark-800'
      }`}>
        {isUser ? (
          <User className="w-5 h-5 text-white" />
        ) : (
          <Bot className="w-5 h-5 text-white" />
        )}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        {/* Header */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className={`text-sm font-semibold ${
              isUser 
                ? 'text-primary-700 dark:text-primary-400' 
                : 'text-dark-700 dark:text-dark-200'
            }`}>
              {isUser ? 'Siz' : 'AI Asistan'}
            </span>
            {message.timestamp && (
              <span className="text-xs text-dark-400 dark:text-dark-500">
                {formatTime(message.timestamp)}
              </span>
            )}
            {/* Response time indicator for AI messages */}
            {!isUser && responseTime && (
              <span className="flex items-center gap-1 text-xs text-dark-400 dark:text-dark-500">
                <Clock className="w-3 h-3" />
                {responseTime.toFixed(1)}s
              </span>
            )}
          </div>

          {/* Copy button */}
          {!isUser && (
            <button
              onClick={handleCopy}
              className="opacity-0 group-hover:opacity-100 p-2 rounded-lg hover:bg-dark-100 dark:hover:bg-dark-700 transition-all duration-200"
              title="Kopyala"
            >
              {copied ? (
                <Check className="w-4 h-4 text-green-500" />
              ) : (
                <Copy className="w-4 h-4 text-dark-400" />
              )}
            </button>
          )}
        </div>

        {/* Image preview if exists */}
        {message.image && (
          <div className="mb-3 inline-block">
            <div className="relative group/image">
              <img
                src={`data:${message.image.media_type};base64,${message.image.base64_data}`}
                alt="Uploaded"
                className="max-w-xs max-h-48 rounded-xl border-2 border-primary-200 dark:border-primary-800 shadow-md"
              />
              <div className="absolute bottom-2 left-2 px-2 py-1 bg-dark-900/70 backdrop-blur-sm rounded-lg flex items-center gap-1">
                <ImageIcon className="w-3 h-3 text-white" />
                <span className="text-xs text-white">Görsel</span>
              </div>
            </div>
          </div>
        )}

        {/* Message content with Markdown support for AI messages */}
        <div className={`message-content text-sm leading-relaxed ${
          isUser 
            ? 'text-dark-800 dark:text-dark-200' 
            : 'text-dark-700 dark:text-dark-300'
        }`}>
          {isUser ? (
            // User messages - plain text with line breaks
            message.content.split('\n').map((line, i) => (
              <p key={i} className={line === '' ? 'h-3' : 'mb-1'}>
                {line}
              </p>
            ))
          ) : (
            // AI messages - full Markdown rendering
            <ReactMarkdown components={markdownComponents}>
              {message.content}
            </ReactMarkdown>
          )}
        </div>

        {/* Model info for AI messages */}
        {!isUser && message.model && (
          <div className="mt-3 flex items-center gap-2">
            <span className="text-xs px-2 py-1 rounded-lg bg-dark-100 dark:bg-dark-700 text-dark-500 dark:text-dark-400">
              {message.model.split('/').pop()?.replace(':free', '')}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
