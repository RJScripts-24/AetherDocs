import { Moon, Sun } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface SessionNavbarProps {
  isDarkMode: boolean;
  toggleTheme: () => void;
}

export function SessionNavbar({ isDarkMode, toggleTheme }: SessionNavbarProps) {
  const navigate = useNavigate();

  return (
    <nav 
      className="sticky top-0 z-50 transition-colors duration-200"
      style={{
        backgroundColor: isDarkMode ? '#2C3930' : '#DCD7C9',
        borderBottom: `1px solid ${isDarkMode ? '#3F4F44' : 'rgba(63, 79, 68, 0.2)'}`
      }}
    >
      <div className="mx-auto px-6 py-4 flex items-center justify-between" style={{ maxWidth: '1440px' }}>
        <button 
          onClick={() => navigate('/')}
          className="flex items-center gap-3 hover:opacity-80 transition-opacity"
        >
          <div 
            className="w-8 h-8 rounded-full flex items-center justify-center"
            style={{
              backgroundColor: isDarkMode ? '#3F4F44' : 'rgba(63, 79, 68, 0.3)',
              border: `2px solid #A27B5C`
            }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" stroke="#A27B5C" strokeWidth="2"/>
              <circle cx="12" cy="12" r="3" fill="#A27B5C"/>
            </svg>
          </div>
          <span 
            className="text-lg font-normal tracking-wide"
            style={{ color: isDarkMode ? '#DCD7C9' : '#2C3930' }}
          >
            AetherDocs
          </span>
        </button>
        
        <div className="flex items-center gap-3 md:gap-6">
          <div 
            className="px-3 md:px-4 py-1.5 rounded-full text-xs md:text-sm"
            style={{
              backgroundColor: isDarkMode ? '#3F4F44' : 'rgba(63, 79, 68, 0.2)',
              color: isDarkMode ? '#DCD7C9' : '#2C3930',
              border: `1px solid ${isDarkMode ? 'rgba(162, 123, 92, 0.2)' : 'rgba(63, 79, 68, 0.3)'}`
            }}
          >
            sess-8392
          </div>
          
          <button 
            className="hidden sm:block text-xs md:text-sm tracking-wide hover:opacity-80 transition-opacity"
            style={{ color: '#A27B5C' }}
          >
            End & Wipe Session
          </button>
          
          <button
            onClick={toggleTheme}
            className="w-9 h-9 md:w-10 md:h-10 rounded-full flex items-center justify-center transition-all hover:opacity-80"
            style={{
              backgroundColor: isDarkMode ? '#3F4F44' : 'rgba(63, 79, 68, 0.3)'
            }}
            aria-label="Toggle theme"
          >
            {isDarkMode ? (
              <Moon size={18} style={{ color: '#A27B5C' }} />
            ) : (
              <Sun size={18} style={{ color: '#A27B5C' }} />
            )}
          </button>
        </div>
      </div>
    </nav>
  );
}