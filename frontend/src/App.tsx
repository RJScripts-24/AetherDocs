import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import { LandingPage } from './pages/LandingPage';
import { SessionPage } from './pages/SessionPage';
import { CommonBookPage } from './pages/CommonBookPage';

export default function App() {
  const [isDarkMode, setIsDarkMode] = useState(true);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', isDarkMode ? 'dark' : 'light');
  }, [isDarkMode]);

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
  };

  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage isDarkMode={isDarkMode} toggleTheme={toggleTheme} />} />
        <Route path="/session" element={<SessionPage isDarkMode={isDarkMode} toggleTheme={toggleTheme} />} />
        <Route path="/common-book" element={<CommonBookPage isDarkMode={isDarkMode} onNavigateHome={() => window.location.href = '/'} toggleTheme={toggleTheme} />} />
      </Routes>
    </Router>
  );
}