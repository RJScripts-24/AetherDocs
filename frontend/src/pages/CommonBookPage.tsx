import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Download, Send, Moon, Sun, Loader2, Maximize2, Minimize2 } from 'lucide-react';
import { PALETTE } from '../styles/palette';
import { DIMENSIONS } from '../styles/dimensions';
import { AetherDocsClient } from '../api/client';
import { toast } from 'sonner';
import type { Citation } from '../api/types';

interface CommonBookPageProps {
  isDarkMode: boolean;
  onNavigateHome: () => void;
  toggleTheme: () => void;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
}

export function CommonBookPage({ isDarkMode, onNavigateHome, toggleTheme }: CommonBookPageProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const sessionId = (location.state as { sessionId?: string })?.sessionId;

  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [pdfUrl, setPdfUrl] = useState<string>('');
  const [isFullscreen, setIsFullscreen] = useState(false);

  useEffect(() => {
    if (!sessionId) {
      toast.error('No session ID found. Redirecting...');
      navigate('/session');
      return;
    }

    // Set PDF URL
    setPdfUrl(`http://localhost:8000/api/v1/download/${sessionId}/commonbook`);
  }, [sessionId, navigate]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || !sessionId) return;

    const userMessage: Message = {
      role: 'user',
      content: inputValue
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await AetherDocsClient.chatQuery({
        session_id: sessionId,
        query: inputValue
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.answer,
        citations: response.citations
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      toast.error('Failed to get response from AI.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRevoke = async () => {
    if (!sessionId) return;

    if (!confirm('Are you sure you want to revoke this session? All data will be permanently deleted.')) {
      return;
    }

    try {
      await AetherDocsClient.revokeSession(sessionId);
      toast.success('Session revoked successfully');
      navigate('/');
    } catch (error) {
      console.error('Revoke error:', error);
      toast.error('Failed to revoke session');
    }
  };

  const handleDownload = () => {
    window.open(pdfUrl, '_blank');
  };

  const handleFullscreenToggle = () => {
    const pdfContainer = document.getElementById('pdf-viewer-container');
    if (!pdfContainer) return;

    if (!isFullscreen) {
      // Enter fullscreen
      if (pdfContainer.requestFullscreen) {
        pdfContainer.requestFullscreen();
      }
    } else {
      // Exit fullscreen
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
  };

  // Listen for fullscreen changes
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
    };
  }, []);

  return (
    <div
      className="min-h-screen flex flex-col"
      style={{
        backgroundColor: isDarkMode ? PALETTE.forestGreen : PALETTE.beige
      }}
    >
      {/* Top Navigation */}
      <nav
        className="border-b"
        style={{
          backgroundColor: isDarkMode ? PALETTE.moss : 'rgba(220, 215, 201, 0.6)',
          borderColor: isDarkMode ? 'rgba(162, 123, 92, 0.15)' : 'rgba(63, 79, 68, 0.2)'
        }}
      >
        <div className="mx-auto px-6 py-3 flex flex-col md:flex-row items-center justify-between gap-3" style={{ maxWidth: DIMENSIONS.maxWidth }}>
          {/* Left - Logo */}
          <button
            onClick={onNavigateHome}
            className="flex items-center gap-3"
          >
            <div
              className="w-7 h-7 rounded-full flex items-center justify-center"
              style={{
                backgroundColor: PALETTE.leather,
                color: PALETTE.beige
              }}
            >
              <span className="text-sm font-medium">A</span>
            </div>
            <span
              className="text-base"
              style={{ color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen }}
            >
              AetherDocs
            </span>
          </button>

          {/* Center - Session Status */}
          <div className="flex flex-wrap items-center justify-center gap-3 md:gap-6">
            <div className="flex items-center gap-2">
              <div
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: PALETTE.success }}
              />
              <span
                className="text-sm"
                style={{ color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen }}
              >
                Session Active
              </span>
            </div>
            <div
              className="px-4 py-1.5 rounded border text-sm font-mono"
              style={{
                backgroundColor: isDarkMode ? 'rgba(44, 57, 48, 0.5)' : 'rgba(63, 79, 68, 0.1)',
                borderColor: isDarkMode ? 'rgba(162, 123, 92, 0.2)' : 'rgba(63, 79, 68, 0.25)',
                color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen
              }}
            >
              {sessionId?.slice(0, 8)}...
            </div>
          </div>

          {/* Right - Action Buttons */}
          <div className="flex flex-wrap items-center justify-center gap-2 md:gap-3">
            <button
              onClick={handleDownload}
              className="flex items-center gap-2 px-3 md:px-4 py-2 rounded text-xs md:text-sm"
              style={{
                backgroundColor: PALETTE.leather,
                color: PALETTE.beige
              }}
            >
              <Download size={16} />
              <span className="hidden sm:inline">Download PDF</span>
              <span className="sm:hidden">Download</span>
            </button>
            <button
              onClick={handleRevoke}
              className="flex items-center gap-2 px-3 md:px-4 py-2 rounded text-xs md:text-sm"
              style={{
                backgroundColor: PALETTE.error,
                color: PALETTE.white
              }}
            >
              <span className="w-2 h-2 rounded-full bg-white" />
              <span className="hidden sm:inline">Revoke Session</span>
              <span className="sm:hidden">Revoke</span>
            </button>
            <button
              className="p-2.5 rounded"
              style={{
                backgroundColor: PALETTE.leather,
                color: PALETTE.beige
              }}
              onClick={toggleTheme}
            >
              {isDarkMode ? <Sun size={18} /> : <Moon size={18} />}
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content - Two Column Layout */}
      <div className="flex-1 w-full mx-auto px-4 md:px-6 py-4 md:py-6" style={{ maxWidth: DIMENSIONS.maxWidth }}>
        <div className="grid grid-cols-1 xl:grid-cols-[1fr_450px] gap-6 h-full">
          {/* Left Column - PDF Viewer */}
          <div className="flex flex-col gap-4">
            <div className="flex items-center gap-3">
              <h2
                className="text-lg"
                style={{
                  color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen,
                  fontWeight: 500
                }}
              >
                Generated Common Book
              </h2>
              <div className="flex items-center gap-2 ml-auto">
                <button
                  onClick={handleFullscreenToggle}
                  className="flex items-center gap-2 px-4 py-2 rounded text-sm"
                  style={{
                    backgroundColor: PALETTE.leather,
                    color: PALETTE.beige
                  }}
                  title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
                >
                  {isFullscreen ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
                  <span>{isFullscreen ? 'Exit' : 'Fullscreen'}</span>
                </button>
                <button
                  onClick={handleDownload}
                  className="flex items-center gap-2 px-4 py-2 rounded text-sm"
                  style={{
                    backgroundColor: PALETTE.leather,
                    color: PALETTE.beige
                  }}
                >
                  <Download size={16} />
                  <span>Download</span>
                </button>
              </div>
            </div>

            {/* PDF iframe */}
            <div
              id="pdf-viewer-container"
              className="rounded-lg border flex-1"
              style={{
                backgroundColor: isDarkMode ? PALETTE.moss : 'rgba(255, 255, 255, 0.4)',
                borderColor: isDarkMode ? 'rgba(162, 123, 92, 0.15)' : 'rgba(63, 79, 68, 0.2)',
                minHeight: '600px'
              }}
            >
              {pdfUrl ? (
                <iframe
                  src={pdfUrl}
                  className="w-full h-full rounded-lg"
                  style={{ minHeight: '600px' }}
                  title="CommonBook PDF"
                />
              ) : (
                <div className="flex items-center justify-center h-full">
                  <p style={{ color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen, opacity: 0.5 }}>
                    Loading PDF...
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Right Column - AI Chat */}
          <div
            className="rounded-lg border flex flex-col"
            style={{
              backgroundColor: isDarkMode ? PALETTE.moss : 'rgba(255, 255, 255, 0.4)',
              borderColor: isDarkMode ? 'rgba(162, 123, 92, 0.15)' : 'rgba(63, 79, 68, 0.2)',
              height: 'calc(100vh - 140px)'
            }}
          >
            {/* Chat Header */}
            <div
              className="px-6 py-4 border-b"
              style={{
                borderColor: isDarkMode ? 'rgba(162, 123, 92, 0.15)' : 'rgba(63, 79, 68, 0.2)'
              }}
            >
              <h2
                className="text-base"
                style={{
                  color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen,
                  fontWeight: 500
                }}
              >
                AI Chat (Powered by Groq)
              </h2>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
              {messages.length === 0 && (
                <div className="text-center py-8">
                  <p style={{ color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen, opacity: 0.5 }}>
                    Ask me anything about your documents!
                  </p>
                </div>
              )}

              {messages.map((msg, idx) => (
                <div key={idx}>
                  <div
                    className="inline-block px-3 py-1 rounded-full text-xs mb-2"
                    style={{
                      backgroundColor: msg.role === 'user'
                        ? (isDarkMode ? 'rgba(44, 57, 48, 0.6)' : 'rgba(63, 79, 68, 0.15)')
                        : PALETTE.leather,
                      color: msg.role === 'user'
                        ? (isDarkMode ? PALETTE.beige : PALETTE.forestGreen)
                        : PALETTE.beige
                    }}
                  >
                    {msg.role === 'user' ? 'You' : 'AetherDocs AI'}
                  </div>
                  <div
                    className="rounded-lg px-4 py-3"
                    style={{
                      backgroundColor: msg.role === 'user'
                        ? (isDarkMode ? 'rgba(44, 57, 48, 0.6)' : 'rgba(220, 215, 201, 0.8)')
                        : (isDarkMode ? 'rgba(162, 123, 92, 0.1)' : 'rgba(162, 123, 92, 0.08)'),
                      border: msg.role === 'assistant'
                        ? `1px solid ${isDarkMode ? 'rgba(162, 123, 92, 0.2)' : 'rgba(162, 123, 92, 0.15)'}`
                        : 'none',
                      color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen
                    }}
                  >
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>

                    {msg.citations && msg.citations.length > 0 && (
                      <div className="mt-3 space-y-1">
                        <p className="text-xs opacity-70">Sources:</p>
                        {msg.citations
                          .filter((cit, idx, arr) => {
                            // Deduplicate: remove citations with same source + page
                            const key = `${cit.source_file}_${cit.page_number}_${cit.timestamp}`;
                            return idx === arr.findIndex(c => `${c.source_file}_${c.page_number}_${c.timestamp}` === key);
                          })
                          .map((cit, citIdx) => (
                            <div
                              key={citIdx}
                              className="text-xs px-2 py-1 rounded"
                              style={{
                                backgroundColor: PALETTE.leather,
                                color: PALETTE.beige,
                                display: 'inline-block',
                                marginRight: '0.5rem'
                              }}
                            >
                              {cit.timestamp
                                ? `Video @ ${cit.timestamp}`
                                : cit.page_number
                                  ? `${cit.source_file} — Page ${cit.page_number}`
                                  : cit.source_file || 'Unknown source'}
                            </div>
                          ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="flex items-center gap-2" style={{ color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen, opacity: 0.7 }}>
                  <Loader2 size={16} className="animate-spin" />
                  <span className="text-sm">AI is thinking...</span>
                </div>
              )}
            </div>

            {/* Chat Input */}
            <div
              className="px-6 py-4 border-t"
              style={{
                borderColor: isDarkMode ? 'rgba(162, 123, 92, 0.15)' : 'rgba(63, 79, 68, 0.2)'
              }}
            >
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Ask a question..."
                  disabled={isLoading}
                  className="flex-1 px-4 py-2.5 rounded border text-sm outline-none"
                  style={{
                    backgroundColor: isDarkMode ? 'rgba(44, 57, 48, 0.4)' : 'rgba(220, 215, 201, 0.6)',
                    borderColor: isDarkMode ? 'rgba(162, 123, 92, 0.2)' : 'rgba(63, 79, 68, 0.2)',
                    color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen
                  }}
                />
                <button
                  onClick={handleSendMessage}
                  disabled={isLoading || !inputValue.trim()}
                  className="p-2.5 rounded disabled:opacity-50"
                  style={{
                    backgroundColor: PALETTE.leather,
                    color: PALETTE.beige
                  }}
                >
                  <Send size={18} />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}