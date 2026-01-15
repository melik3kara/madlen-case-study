import { Sun, Moon } from 'lucide-react';

interface ThemeToggleProps {
  isDark: boolean;
  onToggle: () => void;
}

export function ThemeToggle({ isDark, onToggle }: ThemeToggleProps) {
  return (
    <button
      onClick={onToggle}
      className="relative p-2.5 rounded-xl bg-dark-100 dark:bg-dark-800 hover:bg-dark-200 dark:hover:bg-dark-700 transition-all duration-300 group"
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
    >
      <div className="relative w-5 h-5">
        {/* Sun icon */}
        <Sun 
          className={`w-5 h-5 text-primary-500 absolute inset-0 transition-all duration-300 ${
            isDark ? 'opacity-0 rotate-90 scale-0' : 'opacity-100 rotate-0 scale-100'
          }`}
        />
        {/* Moon icon */}
        <Moon 
          className={`w-5 h-5 text-primary-400 absolute inset-0 transition-all duration-300 ${
            isDark ? 'opacity-100 rotate-0 scale-100' : 'opacity-0 -rotate-90 scale-0'
          }`}
        />
      </div>
      
      {/* Glow effect on hover */}
      <div className={`absolute inset-0 rounded-xl transition-opacity duration-300 opacity-0 group-hover:opacity-100 ${
        isDark ? 'bg-primary-500/10' : 'bg-primary-500/10'
      }`} />
    </button>
  );
}
