import { SessionNavbar } from '../components/session/SessionNavbar';
import { TopUploadPanel } from '../components/session/TopUploadPanel';
import { SessionInputs } from '../components/session/SessionInputs';
import { IntelligenceConfig } from '../components/session/IntelligenceConfig';
import { Footer } from '../components/Footer';
import { useNavigate } from 'react-router-dom';
import { useEffect, useState, useRef } from 'react';
import { AetherDocsClient } from '../api/client';
import { toast } from 'sonner';

interface SessionPageProps {
  isDarkMode: boolean;
  toggleTheme: () => void;
}

export function SessionPage({ isDarkMode, toggleTheme }: SessionPageProps) {
  const navigate = useNavigate();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isSynthesizing, setIsSynthesizing] = useState(false);

  // Shared state for uploaded files
  const [documentFiles, setDocumentFiles] = useState<string[]>([]);
  const [imageFiles, setImageFiles] = useState<string[]>([]);
  const [uploadingFiles, setUploadingFiles] = useState<Set<string>>(new Set());
  const [youtubeUrls, setYoutubeUrls] = useState<string[]>([]);

  const sessionInitRef = useRef(false);

  useEffect(() => {
    if (sessionInitRef.current) return; // Prevent double-init from StrictMode
    sessionInitRef.current = true;

    const initSession = async () => {
      try {
        // Try to restore session from localStorage first
        const savedSessionId = localStorage.getItem('aetherdocs_session_id');
        const savedDocuments = localStorage.getItem('aetherdocs_documents');
        const savedMedia = localStorage.getItem('aetherdocs_media');
        const savedImages = localStorage.getItem('aetherdocs_images');

        if (savedSessionId) {
          // Restore existing session
          console.log('[Session] Restoring session:', savedSessionId);
          setSessionId(savedSessionId);
          if (savedDocuments) setDocumentFiles(JSON.parse(savedDocuments));
          if (savedImages) setImageFiles(JSON.parse(savedImages));
        } else {
          // Create new session
          const response = await AetherDocsClient.startSession();
          console.log('[Session] Created new session:', response.session_id);
          setSessionId(response.session_id);
          localStorage.setItem('aetherdocs_session_id', response.session_id);
        }
      } catch (error) {
        console.error('Failed to initialize session:', error);
        toast.error('Failed to initialize session. Please refresh the page.');
      }
    };

    initSession();
  }, []);

  // Persist file lists to localStorage
  useEffect(() => {
    if (documentFiles.length > 0) {
      localStorage.setItem('aetherdocs_documents', JSON.stringify(documentFiles));
    }
  }, [documentFiles]);



  useEffect(() => {
    if (imageFiles.length > 0) {
      localStorage.setItem('aetherdocs_images', JSON.stringify(imageFiles));
    }
  }, [imageFiles]);

  const clearSession = () => {
    // Clear localStorage
    localStorage.removeItem('aetherdocs_session_id');
    localStorage.removeItem('aetherdocs_documents');
    setDocumentFiles([]);
    setImageFiles([]);
    setSessionId(null);
    setYoutubeUrls([]);

    // Create new session
    AetherDocsClient.startSession().then(response => {
      console.log('[Session] Created new session after reset:', response.session_id);
      setSessionId(response.session_id);
      localStorage.setItem('aetherdocs_session_id', response.session_id);
      toast.success('Session reset successfully');
    });
  };

  const handleFileUpload = async (files: FileList | null, type: 'documents' | 'media' | 'images') => {
    if (!files || !sessionId) {
      if (!sessionId) toast.error("Session not initialized yet.");
      return;
    }

    const fileArray = Array.from(files);
    console.log(`[Upload] Handling ${fileArray.length} files for type: ${type}`);

    for (const file of fileArray) {
      try {
        console.log(`[Upload] Starting upload for: ${file.name} (type: ${file.type})`);
        setUploadingFiles(prev => new Set(prev).add(file.name));

        // Upload file and get metadata from backend
        const metadata = await AetherDocsClient.uploadFile(sessionId, file);
        console.log(`[Upload] Response metadata:`, metadata);

        // Categorize based on actual file type from backend, not UI input
        if (metadata.source_type === 'pdf' || metadata.source_type === 'docx' || metadata.source_type === 'pptx') {
          console.log(`[Upload] Categorizing ${file.name} as document`);
          setDocumentFiles(prev => [...prev, file.name]);
        } else if (metadata.source_type === 'image') {
          console.log(`[Upload] Categorizing ${file.name} as image`);
          setImageFiles(prev => [...prev, file.name]);
        }

        toast.success(`Uploaded ${file.name}`);
      } catch (error) {
        console.error(`Failed to upload ${file.name}`, error);
        toast.error(`Failed to upload ${file.name}`);
      } finally {
        setUploadingFiles(prev => {
          const next = new Set(prev);
          next.delete(file.name);
          return next;
        });
      }
    }
  };

  const handleAddYoutubeUrl = (url: string) => {
    if (url && !youtubeUrls.includes(url)) {
      setYoutubeUrls(prev => [...prev, url]);
      toast.success('Added YouTube URL');
    }
  };

  const handleRemoveYoutubeUrl = (url: string) => {
    setYoutubeUrls(prev => prev.filter(u => u !== url));
  };

  const handleSynthesize = async () => {
    if (!sessionId) {
      toast.error('No active session found.');
      return;
    }

    setIsSynthesizing(true);
    try {
      await AetherDocsClient.triggerSynthesis({
        session_id: sessionId,
        youtube_urls: youtubeUrls.length > 0 ? youtubeUrls : undefined
      });
      toast.success('Synthesis started!');

      // Poll for status
      const pollInterval = setInterval(async () => {
        try {
          const status = await AetherDocsClient.getStatus(sessionId);

          if (status.status === 'completed') {
            clearInterval(pollInterval);
            setIsSynthesizing(false);
            toast.success('Synthesis completed!');

            // Clear session data for next time
            localStorage.removeItem('aetherdocs_session_id');
            localStorage.removeItem('aetherdocs_documents');
            localStorage.removeItem('aetherdocs_images');

            navigate('/common-book', { state: { sessionId } });
          } else if (status.status === 'failed') {
            clearInterval(pollInterval);
            setIsSynthesizing(false);
            toast.error(`Synthesis failed: ${status.error_message}`);
          } else {
            // Show progress
            toast.info(`${status.current_step} (${status.progress_percentage}%)`, { id: 'synthesis-progress' });
          }
        } catch (pollError) {
          console.error('Status poll error:', pollError);
        }
      }, 2000); // Poll every 2 seconds

      // Timeout after 10 minutes
      setTimeout(() => {
        clearInterval(pollInterval);
        if (isSynthesizing) {
          setIsSynthesizing(false);
          toast.error('Synthesis timed out. Please try again.');
        }
      }, 600000);

    } catch (error) {
      console.error('Synthesis failed:', error);
      toast.error('Failed to start synthesis.');
      setIsSynthesizing(false);
    }
  };

  return (
    <div className="min-h-screen transition-colors duration-200 relative" style={{
      backgroundColor: isDarkMode ? '#2C3930' : '#DCD7C9',
      color: isDarkMode ? '#DCD7C9' : '#2C3930'
    }}>
      {/* Radial gradient overlay */}
      <div
        className="fixed inset-0 pointer-events-none"
        style={{
          background: isDarkMode
            ? 'radial-gradient(ellipse at center top, rgba(162, 123, 92, 0.12) 0%, rgba(44, 57, 48, 0) 50%)'
            : 'radial-gradient(ellipse at center top, rgba(162, 123, 92, 0.08) 0%, rgba(220, 215, 201, 0) 50%)'
        }}
      />

      {/* Noise texture overlay */}
      <div
        className="fixed inset-0 pointer-events-none opacity-[0.08]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
          mixBlendMode: isDarkMode ? 'overlay' : 'multiply'
        }}
      />

      {/* Vignette effect */}
      <div
        className="fixed inset-0 pointer-events-none"
        style={{
          background: isDarkMode
            ? 'radial-gradient(circle at center, transparent 0%, rgba(0, 0, 0, 0.4) 100%)'
            : 'radial-gradient(circle at center, transparent 0%, rgba(0, 0, 0, 0.15) 100%)'
        }}
      />

      <div className="relative z-10">
        <SessionNavbar isDarkMode={isDarkMode} toggleTheme={toggleTheme} />

        <div className="mx-auto px-4 md:px-6 py-6 md:py-8" style={{ maxWidth: '1440px' }}>
          <TopUploadPanel
            isDarkMode={isDarkMode}
            documentFiles={documentFiles}
            mediaFiles={[]}
            imageFiles={imageFiles}
            youtubeUrls={youtubeUrls}
            onRemoveYoutubeUrl={handleRemoveYoutubeUrl}
            uploadingFiles={uploadingFiles}
          />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            <SessionInputs
              isDarkMode={isDarkMode}
              sessionId={sessionId}
              onFileUpload={handleFileUpload}
              onAddYoutubeUrl={handleAddYoutubeUrl}
            />
            <IntelligenceConfig isDarkMode={isDarkMode} />
          </div>

          {/* Clear Session Button */}
          <button
            onClick={clearSession}
            className="w-full py-3 rounded-lg text-sm transition-all mt-6"
            style={{
              backgroundColor: 'transparent',
              border: `1px solid ${isDarkMode ? 'rgba(162, 123, 92, 0.3)' : 'rgba(63, 79, 68, 0.3)'}`,
              color: isDarkMode ? '#DCD7C9' : '#2C3930',
            }}
          >
            Clear Session & Start Fresh
          </button>

          <button
            onClick={handleSynthesize}
            disabled={isSynthesizing || !sessionId}
            className="w-full mt-6 px-8 py-4 rounded-lg text-base font-medium transition-all hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
            style={{
              backgroundColor: '#A27B5C',
              color: '#DCD7C9',
              boxShadow: '0 4px 12px rgba(162, 123, 92, 0.3)'
            }}
          >
            {isSynthesizing ? 'Starting Pipeline...' : 'Extract & Synthesize Brain'}
          </button>
        </div>

        <Footer isDarkMode={isDarkMode} />
      </div>
    </div>
  );
}