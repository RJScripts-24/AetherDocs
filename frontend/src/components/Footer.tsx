import { ScrollFadeIn } from './ScrollFadeIn';
import { PALETTE } from '../styles/palette';
import { DIMENSIONS } from '../styles/dimensions';

interface FooterProps {
  isDarkMode: boolean;
}

export function Footer({ isDarkMode }: FooterProps) {
  return (
    <footer className="mx-auto px-4 md:px-6 py-8 md:py-12 text-center" style={{ maxWidth: DIMENSIONS.maxWidth }}>
      <ScrollFadeIn direction="none" delay={0}>
        <p
          className="text-sm italic"
          style={{
            color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen,
            opacity: 0.7
          }}
        >
          Meanwhile,{' '}
          <span style={{ fontStyle: 'italic' }}>the final year at Auto-deep</span>
          . A Storr™ project.
        </p>
      </ScrollFadeIn>
    </footer>
  );
}