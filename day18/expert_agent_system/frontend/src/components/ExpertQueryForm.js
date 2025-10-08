import React, { useState } from 'react';
import { Send, AlertCircle } from 'lucide-react';

const ExpertQueryForm = ({ domains, selectedDomain, onDomainChange, onResult }) => {
  const [query, setQuery] = useState('');
  const [requiredConfidence, setRequiredConfidence] = useState(0.7);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`/query/${selectedDomain}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query.trim(),
          required_confidence: requiredConfidence
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      onResult(result);
    } catch (error) {
      setError(`Failed to process query: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4">Expert Query Interface</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Domain
          </label>
          <select
            value={selectedDomain}
            onChange={(e) => onDomainChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {Object.entries(domains).map(([key, description]) => (
              <option key={key} value={key}>
                {description}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Query
          </label>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your expert-level query..."
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Required Confidence: {requiredConfidence.toFixed(2)}
          </label>
          <input
            type="range"
            min="0.1"
            max="1.0"
            step="0.1"
            value={requiredConfidence}
            onChange={(e) => setRequiredConfidence(parseFloat(e.target.value))}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-gray-500">
            <span>Low (0.1)</span>
            <span>High (1.0)</span>
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading || !query.trim()}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
        >
          {isLoading ? (
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
          ) : (
            <>
              <Send size={20} className="mr-2" />
              Process Query
            </>
          )}
        </button>
      </form>

      {error && (
        <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4 flex items-center">
          <AlertCircle className="text-red-600 mr-2" size={20} />
          <span className="text-red-800">{error}</span>
        </div>
      )}
    </div>
  );
};

export default ExpertQueryForm;
