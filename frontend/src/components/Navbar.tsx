import { Moon, Sun } from 'lucide-react';
import { PALETTE } from '../styles/palette';
import { DIMENSIONS } from '../styles/dimensions';

interface NavbarProps {
  isDarkMode: boolean;
  toggleTheme: () => void;
}

export function Navbar({ isDarkMode, toggleTheme }: NavbarProps) {
  return (
    <nav
      className="sticky top-0 z-50 transition-colors duration-200"
      style={{
        backgroundColor: isDarkMode ? PALETTE.forestGreen : PALETTE.beige,
        borderBottom: `1px solid ${isDarkMode ? PALETTE.moss : 'rgba(63, 79, 68, 0.2)'}`
      }}
    >
      <div className="mx-auto px-6 py-4 flex items-center justify-between" style={{ maxWidth: DIMENSIONS.maxWidth }}>
        <div className="flex items-center gap-3">
          <div
            className="w-8 h-8 rounded-full flex items-center justify-center"
            style={{
              backgroundColor: isDarkMode ? PALETTE.moss : 'rgba(63, 79, 68, 0.3)',
              border: `2px solid #A27B5C`
            }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" stroke="#A27B5C" strokeWidth="2" />
              <circle cx="12" cy="12" r="3" fill="#A27B5C" />
            </svg>
          </div>
          <span
            className="text-lg font-normal tracking-wide"
            style={{ color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen }}
          >
            AetherDocs
          </span>
        </div>

        <div className="flex items-center gap-6">
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden sm:block text-sm tracking-wide hover:opacity-80 transition-opacity"
            style={{ color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen }}
          >
            GitHub
          </a>

          <button
            onClick={toggleTheme}
            className="w-9 h-9 md:w-10 md:h-10 rounded-full flex items-center justify-center transition-all hover:opacity-80"
            style={{
              backgroundColor: isDarkMode ? PALETTE.moss : 'rgba(63, 79, 68, 0.3)'
            }}
            aria-label="Toggle theme"
          >
            {isDarkMode ? (
              <Moon size={18} style={{ color: PALETTE.leather }} />
            ) : (
              <Sun size={18} style={{ color: PALETTE.leather }} />
            )}
          </button>
        </div>
      </div>
    </nav>
  );
}