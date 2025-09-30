import React, { useState, useEffect } from 'react';
import ExpertQueryForm from './components/ExpertQueryForm';
import ValidationResults from './components/ValidationResults';
import AuditTrail from './components/AuditTrail';
import DomainStats from './components/DomainStats';
import './App.css';

function App() {
  const [currentResult, setCurrentResult] = useState(null);
  const [availableDomains, setAvailableDomains] = useState({});
  const [selectedDomain, setSelectedDomain] = useState('technology');
  const [auditQueryId, setAuditQueryId] = useState(null);

  useEffect(() => {
    fetchDomains();
  }, []);

  const fetchDomains = async () => {
    try {
      const response = await fetch('/domains');
      const data = await response.json();
      setAvailableDomains(data.domains);
    } catch (error) {
      console.error('Failed to fetch domains:', error);
    }
  };

  const handleQueryResult = (result) => {
    setCurrentResult(result);
    if (result.query_id) {
      setAuditQueryId(result.query_id);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Expert Agent System
          </h1>
          <p className="text-gray-600">
            AI Agent Specialization & Expertise Validation
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
              <ExpertQueryForm
                domains={availableDomains}
                selectedDomain={selectedDomain}
                onDomainChange={setSelectedDomain}
                onResult={handleQueryResult}
              />
            </div>

            {currentResult && (
              <ValidationResults result={currentResult} />
            )}
          </div>

          <div className="space-y-8">
            <DomainStats domain={selectedDomain} />
            
            {auditQueryId && (
              <AuditTrail queryId={auditQueryId} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
