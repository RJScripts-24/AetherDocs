import { Menu, ChevronDown, Download, Send, MoreVertical, Moon, Sun } from 'lucide-react';
import { PALETTE } from '../styles/palette';
import { DIMENSIONS } from '../styles/dimensions';

interface CommonBookPageProps {
  isDarkMode: boolean;
  onNavigateHome: () => void;
  toggleTheme: () => void;
}

export function CommonBookPage({ isDarkMode, onNavigateHome, toggleTheme }: CommonBookPageProps) {
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
              className="px-4 py-1.5 rounded border text-sm"
              style={{
                backgroundColor: isDarkMode ? 'rgba(44, 57, 48, 0.5)' : 'rgba(63, 79, 68, 0.1)',
                borderColor: isDarkMode ? 'rgba(162, 123, 92, 0.2)' : 'rgba(63, 79, 68, 0.25)',
                color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen
              }}
            >
              sess-8392
            </div>
          </div>

          {/* Right - Action Buttons */}
          <div className="flex flex-wrap items-center justify-center gap-2 md:gap-3">
            <button
              className="flex items-center gap-2 px-3 md:px-4 py-2 rounded text-xs md:text-sm"
              style={{
                backgroundColor: PALETTE.leather,
                color: PALETTE.beige
              }}
            >
              <Download size={16} />
              <span className="hidden sm:inline">Download Common Book (PDF)</span>
              <span className="sm:hidden">Download</span>
            </button>
            <button
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
            {/* Header Controls */}
            <div className="flex items-center gap-3">
              <button
                className="flex items-center gap-3 px-4 py-2.5 rounded border text-sm"
                style={{
                  backgroundColor: isDarkMode ? PALETTE.moss : 'rgba(220, 215, 201, 0.6)',
                  borderColor: isDarkMode ? 'rgba(162, 123, 92, 0.15)' : 'rgba(63, 79, 68, 0.2)',
                  color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen
                }}
              >
                <Menu size={16} />
                <span>Generated PDF</span>
                <ChevronDown size={16} />
              </button>

              <button
                className="flex items-center gap-2 px-4 py-2.5 rounded border text-sm ml-auto"
                style={{
                  backgroundColor: isDarkMode ? PALETTE.moss : 'rgba(220, 215, 201, 0.6)',
                  borderColor: isDarkMode ? 'rgba(162, 123, 92, 0.15)' : 'rgba(63, 79, 68, 0.2)',
                  color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen
                }}
              >
                <Download size={16} />
                <span>Download</span>
                <ChevronDown size={16} />
              </button>
            </div>

            {/* Document Card */}
            <div
              className="rounded-lg border p-8 flex-1 flex items-center justify-center"
              style={{
                backgroundColor: isDarkMode ? PALETTE.moss : 'rgba(255, 255, 255, 0.4)',
                borderColor: isDarkMode ? 'rgba(162, 123, 92, 0.15)' : 'rgba(63, 79, 68, 0.2)'
              }}
            >
              <div className="text-center">
                <div
                  className="w-24 h-24 mx-auto mb-4 rounded-lg flex items-center justify-center"
                  style={{
                    backgroundColor: isDarkMode ? 'rgba(162, 123, 92, 0.1)' : 'rgba(162, 123, 92, 0.08)',
                    border: `2px solid ${isDarkMode ? 'rgba(162, 123, 92, 0.2)' : 'rgba(162, 123, 92, 0.15)'}`
                  }}
                >
                  <svg
                    width="48"
                    height="48"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke={isDarkMode ? PALETTE.beige : PALETTE.forestGreen}
                    strokeWidth="1.5"
                    opacity="0.5"
                  >
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                    <polyline points="14 2 14 8 20 8" />
                    <line x1="16" y1="13" x2="8" y2="13" />
                    <line x1="16" y1="17" x2="8" y2="17" />
                    <polyline points="10 9 9 9 8 9" />
                  </svg>
                </div>
                <p
                  className="text-sm"
                  style={{
                    color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen,
                    opacity: 0.6
                  }}
                >
                  PDF Preview
                </p>
              </div>
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
              className="px-6 py-4 border-b flex items-center justify-between"
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
                AI Chat
              </h2>
              <button style={{ color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen, opacity: 0.6 }}>
                <MoreVertical size={18} />
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
              {/* User Message */}
              <div>
                <div
                  className="inline-block px-3 py-1 rounded-full text-xs mb-2"
                  style={{
                    backgroundColor: isDarkMode ? 'rgba(44, 57, 48, 0.6)' : 'rgba(63, 79, 68, 0.15)',
                    color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen
                  }}
                >
                  User
                </div>
                <div
                  className="rounded-lg px-4 py-3 inline-block max-w-[85%]"
                  style={{
                    backgroundColor: isDarkMode ? 'rgba(44, 57, 48, 0.6)' : 'rgba(220, 215, 201, 0.8)',
                    color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen
                  }}
                >
                  <p className="text-sm">Explain entropy in simple terms.</p>
                </div>
              </div>

              {/* Assistant Message */}
              <div>
                <div
                  className="inline-block px-3 py-1 rounded-full text-xs mb-2"
                  style={{
                    backgroundColor: PALETTE.leather,
                    color: PALETTE.beige
                  }}
                >
                  AetherDocs Tutor
                </div>
                <div
                  className="rounded-lg px-4 py-3"
                  style={{
                    backgroundColor: isDarkMode ? 'rgba(162, 123, 92, 0.1)' : 'rgba(162, 123, 92, 0.08)',
                    border: `1px solid ${isDarkMode ? 'rgba(162, 123, 92, 0.2)' : 'rgba(162, 123, 92, 0.15)'}`,
                    color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen
                  }}
                >
                  <p className="text-sm italic mb-3" style={{ opacity: 0.7 }}>
                    Explain entropy in simple terms.
                  </p>

                  <p className="text-sm leading-relaxed mb-3">
                    Entropy in information theory measures how unpredictable or random a data set is. Think of it as the "surprise" level.{' '}
                    <span
                      className="inline-block px-2 py-0.5 rounded text-xs mx-1"
                      style={{
                        backgroundColor: PALETTE.leather,
                        color: PALETTE.beige
                      }}
                    >
                      Video @ 01:25
                    </span>
                  </p>

                  <p className="text-sm leading-relaxed mb-3">
                    Low entropy means the data is more predictable, like flipping a coin that always lands on heads. High entropy means the data is more uncertain, like flipping a fair coin.{' '}
                    <span
                      className="inline-block px-2 py-0.5 rounded text-xs mx-1"
                      style={{
                        backgroundColor: PALETTE.leather,
                        color: PALETTE.beige
                      }}
                    >
                      Video @ 01:25
                    </span>
                  </p>

                  <p className="text-sm leading-relaxed">
                    In simpler terms, entropy quantifies the amount of uncertainty or disorder in a system.
                  </p>
                </div>
              </div>
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
                  placeholder="Type your question here..."
                  className="flex-1 px-4 py-2.5 rounded border text-sm outline-none"
                  style={{
                    backgroundColor: isDarkMode ? 'rgba(44, 57, 48, 0.4)' : 'rgba(220, 215, 201, 0.6)',
                    borderColor: isDarkMode ? 'rgba(162, 123, 92, 0.2)' : 'rgba(63, 79, 68, 0.2)',
                    color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen
                  }}
                />
                <button
                  className="p-2.5 rounded"
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

      {/* Footer */}
      <footer
        className="py-6 text-center border-t"
        style={{
          borderColor: isDarkMode ? 'rgba(162, 123, 92, 0.1)' : 'rgba(63, 79, 68, 0.15)'
        }}
      >
        <p
          className="text-sm"
          style={{
            color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen,
            opacity: 0.5
          }}
        >
          Meanwhile, the final year at Auto-deep. A Storr™ project.
        </p>
      </footer>
    </div>
  );
}