import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import UploadPage from './pages/UploadPage';
import DocumentView from './pages/DocumentView';
import AuditLogs from './pages/AuditLogs';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/document/:id" element={<DocumentView />} />
            <Route path="/audit" element={<AuditLogs />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
