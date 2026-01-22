import { FileVideo, BookOpen, ShieldCheck } from 'lucide-react';
import { ScrollFadeIn } from './ScrollFadeIn';
import { PALETTE } from '../styles/palette';
import { DIMENSIONS } from '../styles/dimensions';

interface FeatureCardsProps {
  isDarkMode: boolean;
}

export function FeatureCards({ isDarkMode }: FeatureCardsProps) {
  const cards = [
    {
      icon: FileVideo,
      title: 'Multimodal Ingestion',
      subtitle: 'Video / PDF / Audio'
    },
    {
      icon: BookOpen,
      title: 'Smart Deduplication',
      subtitle: 'Unified Study Guides'
    },
    {
      icon: ShieldCheck,
      title: 'Zero Data Retention',
      subtitle: 'No Logs, No Traces'
    }
  ];

  return (
    <section className="mx-auto px-4 md:px-6 pb-16 md:pb-20" style={{ maxWidth: DIMENSIONS.maxWidth }}>
      <ScrollFadeIn direction="none" delay={0}>
        <div className="flex justify-center items-center gap-4 mb-12">
          <div style={{ width: '60px', height: '1px', backgroundColor: isDarkMode ? PALETTE.moss : 'rgba(63, 79, 68, 0.3)' }}></div>
          <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: isDarkMode ? PALETTE.moss : 'rgba(63, 79, 68, 0.3)' }}></div>
          <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: isDarkMode ? PALETTE.moss : 'rgba(63, 79, 68, 0.3)' }}></div>
          <div style={{ width: '60px', height: '1px', backgroundColor: isDarkMode ? PALETTE.moss : 'rgba(63, 79, 68, 0.3)' }}></div>
        </div>
      </ScrollFadeIn>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {cards.map((card, index) => {
          const Icon = card.icon;
          return (
            <ScrollFadeIn key={index} direction="up" delay={index * 0.15}>
              <div
                className="rounded-xl p-8 text-center transition-all"
                style={{
                  backgroundColor: isDarkMode ? PALETTE.moss : 'rgba(220, 215, 201, 0.5)',
                  border: `1px solid ${isDarkMode ? 'rgba(162, 123, 92, 0.2)' : 'rgba(63, 79, 68, 0.2)'}`
                }}
              >
                <div className="flex justify-center mb-5">
                  <div
                    className="p-4 rounded-lg"
                    style={{
                      backgroundColor: isDarkMode ? 'rgba(162, 123, 92, 0.15)' : 'rgba(162, 123, 92, 0.2)'
                    }}
                  >
                    <Icon size={40} style={{ color: PALETTE.leather }} strokeWidth={1.5} />
                  </div>
                </div>

                <h3
                  className="text-lg mb-2"
                  style={{
                    color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen,
                    fontWeight: 500
                  }}
                >
                  {card.title}
                </h3>

                <p
                  className="text-sm"
                  style={{
                    color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen,
                    opacity: 0.8
                  }}
                >
                  {card.subtitle}
                </p>
              </div>
            </ScrollFadeIn>
          );
        })}
      </div>
    </section>
  );
}