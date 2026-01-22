import { SessionNavbar } from '../components/session/SessionNavbar';
import { TopUploadPanel } from '../components/session/TopUploadPanel';
import { SessionInputs } from '../components/session/SessionInputs';
import { IntelligenceConfig } from '../components/session/IntelligenceConfig';
import { Footer } from '../components/Footer';
import { useNavigate } from 'react-router-dom';

interface SessionPageProps {
  isDarkMode: boolean;
  toggleTheme: () => void;
}

export function SessionPage({ isDarkMode, toggleTheme }: SessionPageProps) {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen transition-colors duration-200 relative" style={{
      backgroundColor: isDarkMode ? '#2C3930' : '#DCD7C9',
      color: isDarkMode ? '#DCD7C9' : '#2C3930'
    }}>
      {/* Radial gradient overlay */}
      <div 
        className="fixed inset-0 pointer-events-none"
        style={{
          background: isDarkMode 
            ? 'radial-gradient(ellipse at center top, rgba(162, 123, 92, 0.12) 0%, rgba(44, 57, 48, 0) 50%)'
            : 'radial-gradient(ellipse at center top, rgba(162, 123, 92, 0.08) 0%, rgba(220, 215, 201, 0) 50%)'
        }}
      />
      
      {/* Noise texture overlay */}
      <div 
        className="fixed inset-0 pointer-events-none opacity-[0.08]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
          mixBlendMode: isDarkMode ? 'overlay' : 'multiply'
        }}
      />
      
      {/* Vignette effect */}
      <div 
        className="fixed inset-0 pointer-events-none"
        style={{
          background: isDarkMode
            ? 'radial-gradient(circle at center, transparent 0%, rgba(0, 0, 0, 0.4) 100%)'
            : 'radial-gradient(circle at center, transparent 0%, rgba(0, 0, 0, 0.15) 100%)'
        }}
      />
      
      <div className="relative z-10">
        <SessionNavbar isDarkMode={isDarkMode} toggleTheme={toggleTheme} />
        
        <div className="mx-auto px-4 md:px-6 py-6 md:py-8" style={{ maxWidth: '1440px' }}>
          <TopUploadPanel isDarkMode={isDarkMode} />
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            <SessionInputs isDarkMode={isDarkMode} />
            <IntelligenceConfig isDarkMode={isDarkMode} />
          </div>
          
          <button
            onClick={() => navigate('/common-book')}
            className="w-full mt-6 px-8 py-4 rounded-lg text-base font-medium transition-all hover:opacity-90"
            style={{
              backgroundColor: '#A27B5C',
              color: '#DCD7C9',
              boxShadow: '0 4px 12px rgba(162, 123, 92, 0.3)'
            }}
          >
            Extract & Synthesize Brain
          </button>
        </div>
        
        <Footer isDarkMode={isDarkMode} />
      </div>
    </div>
  );
}