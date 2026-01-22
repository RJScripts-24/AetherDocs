import { useState } from 'react';
import { FileText, X, Info, ChevronRight } from 'lucide-react';

interface SessionInputsProps {
  isDarkMode: boolean;
}

export function SessionInputs({ isDarkMode }: SessionInputsProps) {
  const [activeTab, setActiveTab] = useState<'documents' | 'media' | 'images'>('documents');
  const [files, setFiles] = useState<string[]>(['machine_learning_lecture.pdf']);
  const [mediaExpanded, setMediaExpanded] = useState(true);
  const [imagesExpanded, setImagesExpanded] = useState(true);

  const tabs = [
    { id: 'documents' as const, label: 'Documents' },
    { id: 'media' as const, label: 'Media' },
    { id: 'images' as const, label: 'Images' }
  ];

  const removeFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  return (
    <div 
      className="rounded-xl p-6"
      style={{
        backgroundColor: isDarkMode ? '#3F4F44' : 'rgba(220, 215, 201, 0.4)',
        border: `1px solid ${isDarkMode ? 'rgba(162, 123, 92, 0.15)' : 'rgba(63, 79, 68, 0.2)'}`
      }}
    >
      <div className="flex items-center gap-2 mb-6">
        <h2 
          className="text-lg"
          style={{ 
            color: isDarkMode ? '#DCD7C9' : '#2C3930',
            fontWeight: 400
          }}
        >
          Session ID
        </h2>
        <Info size={16} style={{ color: isDarkMode ? '#DCD7C9' : '#2C3930', opacity: 0.5 }} />
      </div>

      {/* Documents Section */}
      <div className="mb-6">
        <div className="flex gap-1 mb-4 border-b" style={{ borderColor: isDarkMode ? 'rgba(162, 123, 92, 0.2)' : 'rgba(63, 79, 68, 0.2)' }}>
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className="px-4 py-2 text-sm transition-colors"
              style={{
                color: activeTab === tab.id ? '#A27B5C' : (isDarkMode ? '#DCD7C9' : '#2C3930'),
                opacity: activeTab === tab.id ? 1 : 0.6,
                borderBottom: activeTab === tab.id ? '2px solid #A27B5C' : '2px solid transparent',
                marginBottom: '-1px'
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {activeTab === 'documents' && (
          <div>
            <div 
              className="rounded-lg p-6 mb-4 text-center text-sm"
              style={{
                border: `2px dashed ${isDarkMode ? 'rgba(162, 123, 92, 0.3)' : 'rgba(63, 79, 68, 0.3)'}`,
                backgroundColor: isDarkMode ? 'rgba(44, 57, 48, 0.3)' : 'rgba(220, 215, 201, 0.3)',
                color: isDarkMode ? '#DCD7C9' : '#2C3930',
                opacity: 0.7
              }}
            >
              Drag PDFs, DOCX, PPTX here
            </div>

            {files.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between px-3 py-2.5 rounded-lg mb-2"
                style={{
                  backgroundColor: isDarkMode ? 'rgba(162, 123, 92, 0.1)' : 'rgba(162, 123, 92, 0.15)',
                  border: `1px solid ${isDarkMode ? 'rgba(162, 123, 92, 0.2)' : 'rgba(162, 123, 92, 0.25)'}`
                }}
              >
                <div className="flex items-center gap-2 flex-1">
                  <FileText size={16} style={{ color: '#A27B5C' }} />
                  <span 
                    className="text-sm"
                    style={{ color: isDarkMode ? '#DCD7C9' : '#2C3930' }}
                  >
                    {file}
                  </span>
                </div>
                <button
                  className="px-3 py-1 rounded text-xs mr-2"
                  style={{
                    backgroundColor: '#A27B5C',
                    color: '#DCD7C9'
                  }}
                >
                  Fetch
                </button>
              </div>
            ))}

            <button 
              className="text-sm mt-2"
              style={{ color: isDarkMode ? '#DCD7C9' : '#2C3930', opacity: 0.6 }}
            >
              Add another file...
            </button>
          </div>
        )}

        {activeTab === 'media' && (
          <div 
            className="rounded-lg p-6 text-center text-sm"
            style={{
              border: `2px dashed ${isDarkMode ? 'rgba(162, 123, 92, 0.3)' : 'rgba(63, 79, 68, 0.3)'}`,
              backgroundColor: isDarkMode ? 'rgba(44, 57, 48, 0.3)' : 'rgba(220, 215, 201, 0.3)',
              color: isDarkMode ? '#DCD7C9' : '#2C3930',
              opacity: 0.7
            }}
          >
            Drag MP3/MP4 files here
          </div>
        )}

        {activeTab === 'images' && (
          <div 
            className="rounded-lg p-6 text-center text-sm"
            style={{
              border: `2px dashed ${isDarkMode ? 'rgba(162, 123, 92, 0.3)' : 'rgba(63, 79, 68, 0.3)'}`,
              backgroundColor: isDarkMode ? 'rgba(44, 57, 48, 0.3)' : 'rgba(220, 215, 201, 0.3)',
              color: isDarkMode ? '#DCD7C9' : '#2C3930',
              opacity: 0.7
            }}
          >
            Drag charts/diagrams here
          </div>
        )}
      </div>

      {/* Media Section */}
      <div className="mb-6">
        <button
          onClick={() => setMediaExpanded(!mediaExpanded)}
          className="flex items-center gap-2 mb-3 w-full"
        >
          <ChevronRight 
            size={16} 
            style={{ 
              color: isDarkMode ? '#DCD7C9' : '#2C3930',
              transform: mediaExpanded ? 'rotate(90deg)' : 'rotate(0deg)',
              transition: 'transform 0.2s'
            }} 
          />
          <span 
            className="text-sm"
            style={{ color: isDarkMode ? '#DCD7C9' : '#2C3930', fontWeight: 500 }}
          >
            Media
          </span>
        </button>

        {mediaExpanded && (
          <div>
            <div className="flex gap-2 mb-3">
              <input
                type="text"
                placeholder="Paste YouTube URL here"
                className="flex-1 px-3 py-2 rounded text-sm"
                style={{
                  backgroundColor: isDarkMode ? 'rgba(44, 57, 48, 0.5)' : 'rgba(255, 255, 255, 0.5)',
                  border: `1px solid ${isDarkMode ? 'rgba(162, 123, 92, 0.2)' : 'rgba(63, 79, 68, 0.3)'}`,
                  color: isDarkMode ? '#DCD7C9' : '#2C3930'
                }}
              />
              <button
                className="px-4 py-2 rounded text-xs"
                style={{
                  backgroundColor: '#A27B5C',
                  color: '#DCD7C9'
                }}
              >
                Fetch
              </button>
            </div>

            <div 
              className="rounded-lg p-6 text-center text-sm"
              style={{
                border: `2px dashed ${isDarkMode ? 'rgba(162, 123, 92, 0.3)' : 'rgba(63, 79, 68, 0.3)'}`,
                backgroundColor: isDarkMode ? 'rgba(44, 57, 48, 0.3)' : 'rgba(220, 215, 201, 0.3)',
                color: isDarkMode ? '#DCD7C9' : '#2C3930',
                opacity: 0.7
              }}
            >
              Drag MP3/MP4 files here
            </div>
          </div>
        )}
      </div>

      {/* Images Section */}
      <div>
        <button
          onClick={() => setImagesExpanded(!imagesExpanded)}
          className="flex items-center gap-2 mb-3 w-full"
        >
          <ChevronRight 
            size={16} 
            style={{ 
              color: isDarkMode ? '#DCD7C9' : '#2C3930',
              transform: imagesExpanded ? 'rotate(90deg)' : 'rotate(0deg)',
              transition: 'transform 0.2s'
            }} 
          />
          <span 
            className="text-sm"
            style={{ color: isDarkMode ? '#DCD7C9' : '#2C3930', fontWeight: 500 }}
          >
            Images
          </span>
        </button>

        {imagesExpanded && (
          <div 
            className="rounded-lg p-6 text-center text-sm"
            style={{
              border: `2px dashed ${isDarkMode ? 'rgba(162, 123, 92, 0.3)' : 'rgba(63, 79, 68, 0.3)'}`,
              backgroundColor: isDarkMode ? 'rgba(44, 57, 48, 0.3)' : 'rgba(220, 215, 201, 0.3)',
              color: isDarkMode ? '#DCD7C9' : '#2C3930',
              opacity: 0.7
            }}
          >
            Drag charts/diagrams here
          </div>
        )}
      </div>
    </div>
  );
}
