import { useState, useRef } from 'react';
import { FileText, X, Video, Image as ImageIcon, Loader2 } from 'lucide-react';
import { AetherDocsClient } from '../../api/client';
import { toast } from 'sonner';

interface TopUploadPanelProps {
  isDarkMode: boolean;
  sessionId: string | null;
}

export function TopUploadPanel({ isDarkMode, sessionId }: TopUploadPanelProps) {
  const [activeTab, setActiveTab] = useState<'documents' | 'media' | 'images'>('documents');
  const [documentFiles, setDocumentFiles] = useState<string[]>([]);
  const [mediaFiles, setMediaFiles] = useState<string[]>([]);
  const [imageFiles, setImageFiles] = useState<string[]>([]);
  const [uploadingFiles, setUploadingFiles] = useState<Set<string>>(new Set());

  const documentInputRef = useRef<HTMLInputElement>(null);
  const mediaInputRef = useRef<HTMLInputElement>(null);
  const imageInputRef = useRef<HTMLInputElement>(null);

  const tabs = [
    { id: 'documents' as const, label: 'Documents' },
    { id: 'media' as const, label: 'Media' },
    { id: 'images' as const, label: 'Images' }
  ];

  const handleFileSelect = async (files: FileList | null, type: 'documents' | 'media' | 'images') => {
    if (!files || !sessionId) {
      if (!sessionId) toast.error("Session not initialized yet.");
      return;
    }

    const fileArray = Array.from(files);

    for (const file of fileArray) {
      try {
        setUploadingFiles(prev => new Set(prev).add(file.name));

        // Optimistic update
        if (type === 'documents') setDocumentFiles(prev => [...prev, file.name]);
        else if (type === 'media') setMediaFiles(prev => [...prev, file.name]);
        else if (type === 'images') setImageFiles(prev => [...prev, file.name]);

        await AetherDocsClient.uploadFile(sessionId, file);
        toast.success(`Uploaded ${file.name}`);
      } catch (error) {
        console.error(`Failed to upload ${file.name}`, error);
        toast.error(`Failed to upload ${file.name}`);

        // Rollback on error
        if (type === 'documents') setDocumentFiles(prev => prev.filter(f => f !== file.name));
        else if (type === 'media') setMediaFiles(prev => prev.filter(f => f !== file.name));
        else if (type === 'images') setImageFiles(prev => prev.filter(f => f !== file.name));
      } finally {
        setUploadingFiles(prev => {
          const next = new Set(prev);
          next.delete(file.name);
          return next;
        });
      }
    }
  };

  const handleDrop = (e: React.DragEvent, type: 'documents' | 'media' | 'images') => {
    e.preventDefault();
    handleFileSelect(e.dataTransfer.files, type);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const removeFile = (index: number, type: 'documents' | 'media' | 'images') => {
    if (type === 'documents') {
      setDocumentFiles(prev => prev.filter((_, i) => i !== index));
    } else if (type === 'media') {
      setMediaFiles(prev => prev.filter((_, i) => i !== index));
    } else if (type === 'images') {
      setImageFiles(prev => prev.filter((_, i) => i !== index));
    }
  };

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
            <button
              onClick={() => removeFile(index, type)}
              className="p-1 rounded hover:opacity-80 transition-opacity"
              style={{ color: isDarkMode ? '#DCD7C9' : '#2C3930', opacity: 0.6 }}
            >
              <X size={16} />
            </button>
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

      {/* Hidden file inputs */}
      <input
        ref={documentInputRef}
        type="file"
        multiple
        accept=".pdf,.doc,.docx,.ppt,.pptx"
        onChange={(e) => handleFileSelect(e.target.files, 'documents')}
        className="hidden"
      />
      <input
        ref={mediaInputRef}
        type="file"
        multiple
        accept="audio/*,video/*,.mp3,.mp4"
        onChange={(e) => handleFileSelect(e.target.files, 'media')}
        className="hidden"
      />
      <input
        ref={imageInputRef}
        type="file"
        multiple
        accept="image/*"
        onChange={(e) => handleFileSelect(e.target.files, 'images')}
        className="hidden"
      />

      {activeTab === 'documents' && (
        <div>
          {documentFiles.length > 0 && (
            <>
              <h3
                className="text-sm mb-3"
                style={{
                  color: isDarkMode ? '#DCD7C9' : '#2C3930',
                  fontWeight: 500
                }}
              >
                Your Uploaded files
              </h3>
              {renderFileList(documentFiles, 'documents')}
            </>
          )}

          <button
            className="text-sm mt-2 hover:opacity-80 transition-opacity"
            style={{ color: isDarkMode ? '#DCD7C9' : '#2C3930', opacity: 0.6 }}
            onClick={() => documentInputRef.current?.click()}
          >
            Add another file...
          </button>
        </div>
      )}

      {activeTab === 'media' && (
        <div>
          <div
            className="rounded-lg p-8 mb-4 text-center cursor-pointer hover:opacity-80 transition-opacity"
            style={{
              border: `2px dashed ${isDarkMode ? 'rgba(162, 123, 92, 0.3)' : 'rgba(63, 79, 68, 0.3)'}`,
              backgroundColor: isDarkMode ? 'rgba(44, 57, 48, 0.3)' : 'rgba(220, 215, 201, 0.3)'
            }}
            onDrop={(e) => handleDrop(e, 'media')}
            onDragOver={handleDragOver}
            onClick={() => mediaInputRef.current?.click()}
          >
            <p
              className="text-sm"
              style={{
                color: isDarkMode ? '#DCD7C9' : '#2C3930',
                opacity: 0.7
              }}
            >
              Drag MP3/MP4 files here
            </p>
          </div>

          {mediaFiles.length > 0 && (
            <>
              <h3
                className="text-sm mb-3"
                style={{
                  color: isDarkMode ? '#DCD7C9' : '#2C3930',
                  fontWeight: 500
                }}
              >
                Your Uploaded files
              </h3>
              {renderFileList(mediaFiles, 'media')}
              <button
                className="text-sm mt-2 hover:opacity-80 transition-opacity"
                style={{ color: isDarkMode ? '#DCD7C9' : '#2C3930', opacity: 0.6 }}
                onClick={() => mediaInputRef.current?.click()}
              >
                Add another file...
              </button>
            </>
          )}
        </div>
      )}

      {activeTab === 'images' && (
        <div>
          <div
            className="rounded-lg p-8 mb-4 text-center cursor-pointer hover:opacity-80 transition-opacity"
            style={{
              border: `2px dashed ${isDarkMode ? 'rgba(162, 123, 92, 0.3)' : 'rgba(63, 79, 68, 0.3)'}`,
              backgroundColor: isDarkMode ? 'rgba(44, 57, 48, 0.3)' : 'rgba(220, 215, 201, 0.3)'
            }}
            onDrop={(e) => handleDrop(e, 'images')}
            onDragOver={handleDragOver}
            onClick={() => imageInputRef.current?.click()}
          >
            <p
              className="text-sm"
              style={{
                color: isDarkMode ? '#DCD7C9' : '#2C3930',
                opacity: 0.7
              }}
            >
              Drag charts/diagrams here
            </p>
          </div>

          {imageFiles.length > 0 && (
            <>
              <h3
                className="text-sm mb-3"
                style={{
                  color: isDarkMode ? '#DCD7C9' : '#2C3930',
                  fontWeight: 500
                }}
              >
                Your Uploaded files
              </h3>
              {renderFileList(imageFiles, 'images')}
              <button
                className="text-sm mt-2 hover:opacity-80 transition-opacity"
                style={{ color: isDarkMode ? '#DCD7C9' : '#2C3930', opacity: 0.6 }}
                onClick={() => imageInputRef.current?.click()}
              >
                Add another file...
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
}