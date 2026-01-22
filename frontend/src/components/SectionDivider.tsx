import { ScrollFadeIn } from './ScrollFadeIn';
import { PALETTE } from '../styles/palette';
import { DIMENSIONS } from '../styles/dimensions';

interface SectionDividerProps {
  isDarkMode: boolean;
}

export function SectionDivider({ isDarkMode }: SectionDividerProps) {
  return (
    <section className="mx-auto px-4 md:px-6 pb-12 md:pb-16" style={{ maxWidth: DIMENSIONS.maxWidth }}>
      <ScrollFadeIn direction="none" delay={0}>
        <div className="flex justify-center items-center gap-4 mb-6">
          <div style={{ width: '80px', height: '1px', backgroundColor: isDarkMode ? PALETTE.moss : 'rgba(63, 79, 68, 0.3)' }}></div>
          <div style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: PALETTE.leather }}></div>
          <div style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: PALETTE.leather }}></div>
          <div style={{ width: '80px', height: '1px', backgroundColor: isDarkMode ? PALETTE.moss : 'rgba(63, 79, 68, 0.3)' }}></div>
        </div>
      </ScrollFadeIn>

      <ScrollFadeIn direction="up" delay={0.2}>
        <h2
          className="text-3xl md:text-4xl text-center tracking-tight"
          style={{
            color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen,
            fontWeight: 400,
            letterSpacing: '-0.01em'
          }}
        >
          Experience Effortless Learning, With Total Privacy
        </h2>
      </ScrollFadeIn>

      <ScrollFadeIn direction="none" delay={0.3}>
        <div className="flex justify-center items-center gap-4 mt-6">
          <div style={{ width: '80px', height: '1px', backgroundColor: isDarkMode ? PALETTE.moss : 'rgba(63, 79, 68, 0.3)' }}></div>
          <div style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: PALETTE.leather }}></div>
          <div style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: PALETTE.leather }}></div>
          <div style={{ width: '80px', height: '1px', backgroundColor: isDarkMode ? PALETTE.moss : 'rgba(63, 79, 68, 0.3)' }}></div>
        </div>
      </ScrollFadeIn>
    </section>
  );
}