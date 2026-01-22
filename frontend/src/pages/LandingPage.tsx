import { useNavigate } from 'react-router-dom';
import { PALETTE } from '../styles/palette';
import { Navbar } from '../components/Navbar';
import { Hero } from '../components/Hero';
import { FeatureCards } from '../components/FeatureCards';
import { SectionDivider } from '../components/SectionDivider';
import { FeatureBlocks } from '../components/FeatureBlocks';
import { Footer } from '../components/Footer';

interface LandingPageProps {
  isDarkMode: boolean;
  toggleTheme: () => void;
}

export function LandingPage({ isDarkMode, toggleTheme }: LandingPageProps) {
  const navigate = useNavigate();

  const handleStartSession = () => {
    navigate('/session');
  };

  return (
    <div className="min-h-screen transition-colors duration-200 relative" style={{
      backgroundColor: isDarkMode ? PALETTE.forestGreen : PALETTE.beige,
      color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen
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
        <Navbar isDarkMode={isDarkMode} toggleTheme={toggleTheme} />
        <Hero isDarkMode={isDarkMode} onStartSession={handleStartSession} />
        <FeatureCards isDarkMode={isDarkMode} />
        <SectionDivider isDarkMode={isDarkMode} />
        <FeatureBlocks isDarkMode={isDarkMode} />
        <Footer isDarkMode={isDarkMode} />
      </div>
    </div>
  );
}
