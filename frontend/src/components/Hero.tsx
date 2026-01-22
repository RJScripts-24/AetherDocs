import { ScrollFadeIn } from './ScrollFadeIn';
import { PALETTE } from '../styles/palette';
import { DIMENSIONS } from '../styles/dimensions';

interface HeroProps {
  isDarkMode: boolean;
  onStartSession: () => void;
}

export function Hero({ isDarkMode, onStartSession }: HeroProps) {
  return (
    <section className="mx-auto px-4 md:px-6 pt-12 md:pt-16 pb-16 md:pb-20 text-center" style={{ maxWidth: DIMENSIONS.maxWidth }}>
      <ScrollFadeIn direction="up" delay={0.1}>
        <h1
          className="text-4xl md:text-5xl mb-6 tracking-tight"
          style={{
            color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen,
            fontWeight: 400,
            letterSpacing: '-0.02em'
          }}
        >
          Your Private, Ephemeral AI Study Partner.
        </h1>
      </ScrollFadeIn>

      <ScrollFadeIn direction="up" delay={0.2}>
        <p
          className="text-base md:text-lg mb-3 max-w-2xl mx-auto leading-relaxed"
          style={{
            color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen,
            opacity: 0.9
          }}
        >
          Upload lectures, PDFs, and notes. Get a unified study guide and an interactive tutor.
        </p>
      </ScrollFadeIn>

      <ScrollFadeIn direction="up" delay={0.3}>
        <p
          className="text-base md:text-lg mb-10 max-w-2xl mx-auto leading-relaxed"
          style={{
            color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen,
            opacity: 0.9
          }}
        >
          No sign-up. Data vanishes when you leave.
        </p>
      </ScrollFadeIn>

      <ScrollFadeIn direction="up" delay={0.4}>
        <button
          onClick={onStartSession}
          className="px-8 py-3.5 rounded-lg text-base font-medium transition-all hover:opacity-90 hover:scale-105"
          style={{
            backgroundColor: PALETTE.leather,
            color: PALETTE.beige,
            boxShadow: '0 4px 12px rgba(162, 123, 92, 0.3)'
          }}
        >
          Start Temporary Session
        </button>
      </ScrollFadeIn>
    </section>
  );
}