import { useState, useRef } from 'react';
import { FileText, X, Info, ChevronRight } from 'lucide-react';

interface SessionInputsProps {
  isDarkMode: boolean;
  sessionId: string | null;
  onFileUpload: (files: FileList | null, type: 'documents' | 'media' | 'images') => Promise<void>;
}

export function SessionInputs({ isDarkMode, sessionId, onFileUpload }: SessionInputsProps) {
  const [activeTab, setActiveTab] = useState<'documents' | 'media' | 'images'>('documents');
  const [mediaExpanded, setMediaExpanded] = useState(true);
  const [imagesExpanded, setImagesExpanded] = useState(true);

  const documentInputRef = useRef<HTMLInputElement>(null);
  const mediaInputRef = useRef<HTMLInputElement>(null);
  const imageInputRef = useRef<HTMLInputElement>(null);

  const tabs = [
    { id: 'documents' as const, label: 'Documents' },
    { id: 'media' as const, label: 'Media' },
    { id: 'images' as const, label: 'Images' }
  ];

  const handleDrop = (e: React.DragEvent, type: 'documents' | 'media' | 'images') => {
    e.preventDefault();
    onFileUpload(e.dataTransfer.files, type);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
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
          Upload Files
        </h2>
        <Info size={16} style={{ color: isDarkMode ? '#DCD7C9' : '#2C3930', opacity: 0.5 }} />
      </div>

      {/* Hidden file inputs */}
      <input
        ref={documentInputRef}
        type="file"
        multiple
        accept=".pdf,.doc,.docx,.ppt,.pptx"
        onChange={(e) => onFileUpload(e.target.files, 'documents')}
        className="hidden"
      />
      <input
        ref={mediaInputRef}
        type="file"
        multiple
        accept="audio/*,video/*,.mp3,.mp4"
        onChange={(e) => onFileUpload(e.target.files, 'media')}
        className="hidden"
      />
      <input
        ref={imageInputRef}
        type="file"
        multiple
        accept="image/*"
        onChange={(e) => onFileUpload(e.target.files, 'images')}
        className="hidden"
      />

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
          <div
            className="rounded-lg p-8 text-center text-sm cursor-pointer hover:opacity-80 transition-opacity"
            style={{
              border: `2px dashed ${isDarkMode ? 'rgba(162, 123, 92, 0.3)' : 'rgba(63, 79, 68, 0.3)'}`,
              backgroundColor: isDarkMode ? 'rgba(44, 57, 48, 0.3)' : 'rgba(220, 215, 201, 0.3)',
              color: isDarkMode ? '#DCD7C9' : '#2C3930',
              opacity: 0.7
            }}
            onDrop={(e) => handleDrop(e, 'documents')}
            onDragOver={handleDragOver}
            onClick={() => documentInputRef.current?.click()}
          >
            Drag PDF/DOC/PPT files here or click to browse
          </div>
        )}

        {activeTab === 'media' && (
          <div
            className="rounded-lg p-8 text-center text-sm cursor-pointer hover:opacity-80 transition-opacity"
            style={{
              border: `2px dashed ${isDarkMode ? 'rgba(162, 123, 92, 0.3)' : 'rgba(63, 79, 68, 0.3)'}`,
              backgroundColor: isDarkMode ? 'rgba(44, 57, 48, 0.3)' : 'rgba(220, 215, 201, 0.3)',
              color: isDarkMode ? '#DCD7C9' : '#2C3930',
              opacity: 0.7
            }}
            onDrop={(e) => handleDrop(e, 'media')}
            onDragOver={handleDragOver}
            onClick={() => mediaInputRef.current?.click()}
          >
            Drag MP3/MP4 files here or click to browse
          </div>
        )}

        {activeTab === 'images' && (
          <div
            className="rounded-lg p-8 text-center text-sm cursor-pointer hover:opacity-80 transition-opacity"
            style={{
              border: `2px dashed ${isDarkMode ? 'rgba(162, 123, 92, 0.3)' : 'rgba(63, 79, 68, 0.3)'}`,
              backgroundColor: isDarkMode ? 'rgba(44, 57, 48, 0.3)' : 'rgba(220, 215, 201, 0.3)',
              color: isDarkMode ? '#DCD7C9' : '#2C3930',
              opacity: 0.7
            }}
            onDrop={(e) => handleDrop(e, 'images')}
            onDragOver={handleDragOver}
            onClick={() => imageInputRef.current?.click()}
          >
            Drag charts/diagrams here or click to browse
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
            YouTube URL
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
          </div>
        )}
      </div>
    </div>
  );
}
