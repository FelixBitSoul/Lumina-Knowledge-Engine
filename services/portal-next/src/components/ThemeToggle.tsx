'use client';

import { useTheme } from 'next-themes';
import { Sun, Moon } from 'lucide-react';
import { useState, useEffect } from 'react';

const ThemeToggle: React.FC = () => {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // 避免 Hydration 错误，等待组件挂载后再显示
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    // 服务器端渲染时返回一个固定的图标，与默认主题一致
    return (
      <button
        onClick={() => setTheme('light')}
        className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
        aria-label="Toggle Theme"
      >
        <Sun className="text-yellow-400" size={16} />
      </button>
    );
  }

  return (
    <button
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
      className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
      aria-label="Toggle Theme"
    >
      {theme === 'dark' ? (
        <Sun className="text-yellow-400" size={16} />
      ) : (
        <Moon className="text-blue-600" size={16} />
      )}
    </button>
  );
};

export default ThemeToggle;
