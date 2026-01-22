import { FileVideo, BookOpen, MessageCircle, Flame } from 'lucide-react';
import { ScrollFadeIn } from './ScrollFadeIn';
import { PALETTE } from '../styles/palette';
import { DIMENSIONS } from '../styles/dimensions';

interface FeatureBlocksProps {
  isDarkMode: boolean;
}

export function FeatureBlocks({ isDarkMode }: FeatureBlocksProps) {
  const blocks = [
    {
      icon: FileVideo,
      title: 'Multimodal Ingestion Engine',
      description: 'Ingest Video, PDF, DOCX, PPTX, MP3 audio, and even YouTube URL\'s directly. Charts and images inside PDFs are fully understood using vision models, ensuring no data is missed.'
    },
    {
      icon: BookOpen,
      title: 'Smart Deduplication Synthesis',
      description: 'Get a unified, deduplication-free study guide. AetherDocs compares content from every source, removing repetition and compiling essential knowledge.'
    },
    {
      icon: MessageCircle,
      title: 'Contextual AI Tutor',
      description: 'Chat with an interactive tutor that references your materials with strict citations (timestamps, page numbers). Ask any study question and get instant, accurate answers.'
    },
    {
      icon: Flame,
      title: 'Burner-style Privacy & Data Wipe',
      description: 'Your session is temporary, with no sign-ups or databases. Once you end the session, all your files and data are instantly and permanently deleted from the server.'
    }
  ];

  return (
    <section className="mx-auto px-4 md:px-6 pb-16 md:pb-20" style={{ maxWidth: DIMENSIONS.maxWidth }}>
      <div className="space-y-6">
        {blocks.map((block, index) => {
          const Icon = block.icon;
          return (
            <ScrollFadeIn key={index} direction="up" delay={index * 0.1}>
              <div
                className="rounded-xl p-6 flex gap-6 items-start transition-all"
                style={{
                  backgroundColor: isDarkMode ? PALETTE.moss : 'rgba(220, 215, 201, 0.4)',
                  border: `1px solid ${isDarkMode ? 'rgba(162, 123, 92, 0.15)' : 'rgba(63, 79, 68, 0.2)'}`
                }}
              >
                <div
                  className="flex-shrink-0 p-3 rounded-lg"
                  style={{
                    backgroundColor: isDarkMode ? 'rgba(162, 123, 92, 0.15)' : 'rgba(162, 123, 92, 0.2)'
                  }}
                >
                  <Icon size={36} style={{ color: PALETTE.leather }} strokeWidth={1.5} />
                </div>

                <div className="flex-1 pt-1">
                  <h3
                    className="text-xl mb-3"
                    style={{
                      color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen,
                      fontWeight: 500
                    }}
                  >
                    {block.title}
                  </h3>

                  <p
                    className="text-sm leading-relaxed"
                    style={{
                      color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen,
                      opacity: 0.85,
                      lineHeight: '1.7'
                    }}
                  >
                    {block.description}
                  </p>
                </div>
              </div>
            </ScrollFadeIn>
          );
        })}
      </div>
    </section>
  );
}