import { useState } from 'react';
import { FileText, X, Video, Image as ImageIcon, Loader2 } from 'lucide-react';

interface TopUploadPanelProps {
  isDarkMode: boolean;
  documentFiles: string[];
  mediaFiles: string[];
  imageFiles: string[];
  uploadingFiles: Set<string>;
}

export function TopUploadPanel({
  isDarkMode,
  documentFiles,
  mediaFiles,
  imageFiles,
  uploadingFiles
}: TopUploadPanelProps) {
  const [activeTab, setActiveTab] = useState<'documents' | 'media' | 'images'>('documents');

  const tabs = [
    { id: 'documents' as const, label: 'Documents' },
    { id: 'media' as const, label: 'Media' },
    { id: 'images' as const, label: 'Images' }
  ];

  const getFileIcon = (fileName: string, type: string) => {
    if (type === 'media') return Video;
    if (type === 'images') return ImageIcon;
    return FileText;
  };

  const renderFileList = (files: string[], type: 'documents' | 'media' | 'images') => (
    <>
      {files.map((file, index) => {
        const Icon = getFileIcon(file, type);
        const isUploading = uploadingFiles.has(file);

        return (
          <div
            key={index}
            className="flex items-center justify-between px-4 py-3 rounded-lg mb-2"
            style={{
              backgroundColor: isDarkMode ? 'rgba(162, 123, 92, 0.1)' : 'rgba(162, 123, 92, 0.15)',
              border: `1px solid ${isDarkMode ? 'rgba(162, 123, 92, 0.2)' : 'rgba(162, 123, 92, 0.25)'}`
            }}
          >
            <div className="flex items-center gap-3">
              <Icon size={18} style={{ color: '#A27B5C' }} />
              <span
                className="text-sm"
                style={{ color: isDarkMode ? '#DCD7C9' : '#2C3930' }}
              >
                {file}
              </span>
              {isUploading && <Loader2 size={14} className="animate-spin text-gray-500" />}
            </div>
          </div>
        );
      })}
    </>
  );

  return (
    <div
      className="rounded-xl p-6"
      style={{
        backgroundColor: isDarkMode ? '#3F4F44' : 'rgba(220, 215, 201, 0.4)',
        border: `1px solid ${isDarkMode ? 'rgba(162, 123, 92, 0.15)' : 'rgba(63, 79, 68, 0.2)'}`
      }}
    >
      <h2
        className="text-lg mb-4"
        style={{
          color: isDarkMode ? '#DCD7C9' : '#2C3930',
          fontWeight: 400
        }}
      >
        Uploaded Files
      </h2>

      <div className="flex gap-1 mb-6 border-b" style={{ borderColor: isDarkMode ? 'rgba(162, 123, 92, 0.2)' : 'rgba(63, 79, 68, 0.2)' }}>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className="px-6 py-2.5 text-sm transition-colors"
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
          {documentFiles.length > 0 ? (
            renderFileList(documentFiles, 'documents')
          ) : (
            <p
              className="text-sm text-center py-8"
              style={{
                color: isDarkMode ? '#DCD7C9' : '#2C3930',
                opacity: 0.5
              }}
            >
              No documents uploaded yet
            </p>
          )}
        </div>
      )}

      {activeTab === 'media' && (
        <div>
          {mediaFiles.length > 0 ? (
            renderFileList(mediaFiles, 'media')
          ) : (
            <p
              className="text-sm text-center py-8"
              style={{
                color: isDarkMode ? '#DCD7C9' : '#2C3930',
                opacity: 0.5
              }}
            >
              No media files uploaded yet
            </p>
          )}
        </div>
      )}

      {activeTab === 'images' && (
        <div>
          {imageFiles.length > 0 ? (
            renderFileList(imageFiles, 'images')
          ) : (
            <p
              className="text-sm text-center py-8"
              style={{
                color: isDarkMode ? '#DCD7C9' : '#2C3930',
                opacity: 0.5
              }}
            >
              No images uploaded yet
            </p>
          )}
        </div>
      )}
    </div>
  );
}