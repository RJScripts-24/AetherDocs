import { useState } from 'react';
import { Rocket, Brain } from 'lucide-react';

interface IntelligenceConfigProps {
  isDarkMode: boolean;
}

export function IntelligenceConfig({ isDarkMode }: IntelligenceConfigProps) {
  const [selectedMode, setSelectedMode] = useState<'speed' | 'deep'>('speed');

  const configs = [
    {
      id: 'speed' as const,
      icon: Rocket,
      title: 'Speed',
      model: 'Llama-3-8b',
      description: 'Fast summaries.\nGood for skimming.'
    },
    {
      id: 'deep' as const,
      icon: Brain,
      title: 'Deep Dive',
      model: 'Llama-3-70b',
      description: 'Comprehensive analysis.\nCaptures nuances.'
    }
  ];

  return (
    <div 
      className="rounded-xl p-6"
      style={{
        backgroundColor: isDarkMode ? '#3F4F44' : 'rgba(220, 215, 201, 0.4)',
        border: `1px solid ${isDarkMode ? 'rgba(162, 123, 92, 0.15)' : 'rgba(63, 79, 68, 0.2)'}`
      }}
    >
      <h2 
        className="text-lg mb-6"
        style={{ 
          color: isDarkMode ? '#DCD7C9' : '#2C3930',
          fontWeight: 400
        }}
      >
        Intelligence Config
      </h2>

      <h3 
        className="text-sm mb-4"
        style={{ 
          color: isDarkMode ? '#DCD7C9' : '#2C3930',
          fontWeight: 500
        }}
      >
        Select Depth
      </h3>

      <div className="space-y-4">
        {configs.map((config) => {
          const Icon = config.icon;
          const isSelected = selectedMode === config.id;
          
          return (
            <button
              key={config.id}
              onClick={() => setSelectedMode(config.id)}
              className="w-full rounded-lg p-4 flex items-start gap-4 text-left transition-all"
              style={{
                backgroundColor: isSelected 
                  ? (isDarkMode ? 'rgba(162, 123, 92, 0.15)' : 'rgba(162, 123, 92, 0.2)')
                  : (isDarkMode ? 'rgba(44, 57, 48, 0.3)' : 'rgba(220, 215, 201, 0.3)'),
                border: `2px solid ${isSelected ? '#A27B5C' : (isDarkMode ? 'rgba(162, 123, 92, 0.2)' : 'rgba(63, 79, 68, 0.2)')}`
              }}
            >
              <div 
                className="p-2 rounded-lg flex-shrink-0"
                style={{
                  backgroundColor: isDarkMode ? 'rgba(162, 123, 92, 0.2)' : 'rgba(162, 123, 92, 0.25)'
                }}
              >
                <Icon size={24} style={{ color: '#A27B5C' }} strokeWidth={1.5} />
              </div>

              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <h4 
                    className="text-base"
                    style={{ 
                      color: isDarkMode ? '#DCD7C9' : '#2C3930',
                      fontWeight: 500
                    }}
                  >
                    {config.title}
                  </h4>
                  <div
                    className="w-5 h-5 rounded-full flex items-center justify-center"
                    style={{
                      border: `2px solid ${isSelected ? '#A27B5C' : (isDarkMode ? 'rgba(220, 215, 201, 0.3)' : 'rgba(44, 57, 48, 0.3)')}`
                    }}
                  >
                    {isSelected && (
                      <div
                        className="w-2.5 h-2.5 rounded-full"
                        style={{ backgroundColor: '#A27B5C' }}
                      />
                    )}
                  </div>
                </div>

                <p 
                  className="text-xs mb-2"
                  style={{ 
                    color: isDarkMode ? '#DCD7C9' : '#2C3930',
                    opacity: 0.7
                  }}
                >
                  {config.model}
                </p>

                <p 
                  className="text-sm whitespace-pre-line"
                  style={{ 
                    color: isDarkMode ? '#DCD7C9' : '#2C3930',
                    opacity: 0.85,
                    lineHeight: '1.5'
                  }}
                >
                  {config.description}
                </p>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
