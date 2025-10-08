import React from 'react';
import { AlertTriangle, CheckCircle, Info, Shield } from 'lucide-react';

const ResultsPanel = ({ results }) => {
  if (!results.length) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-8 text-center">
        <Shield className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-500">No analysis results yet. Upload a file to get started.</p>
      </div>
    );
  }

  const getThreatLevelIcon = (level) => {
    switch(level) {
      case 'LOW':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'MEDIUM':
        return <Info className="w-5 h-5 text-yellow-600" />;
      case 'HIGH':
      case 'CRITICAL':
        return <AlertTriangle className="w-5 h-5 text-red-600" />;
      default:
        return <Shield className="w-5 h-5 text-gray-600" />;
    }
  };

  const getThreatLevelColor = (level) => {
    const colors = {
      LOW: 'border-green-200 bg-green-50',
      MEDIUM: 'border-yellow-200 bg-yellow-50',
      HIGH: 'border-red-200 bg-red-50',
      CRITICAL: 'border-red-300 bg-red-100'
    };
    return colors[level] || 'border-gray-200 bg-gray-50';
  };

  return (
    <div className="bg-white rounded-lg shadow-sm">
      <div className="px-6 py-4 border-b">
        <h2 className="text-lg font-semibold text-gray-900">Analysis Results</h2>
      </div>
      
      <div className="p-6">
        <div className="space-y-4">
          {results.map((result, index) => (
            <div key={index} className={`border-2 rounded-lg p-4 ${getThreatLevelColor(result.threat_level)}`}>
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-medium text-gray-900">{result.filename}</h3>
                <div className="flex items-center space-x-2">
                  {getThreatLevelIcon(result.threat_level)}
                  <span className="text-sm font-medium">{result.threat_level} Risk</span>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                  <span className="text-sm text-gray-500">Risk Score</span>
                  <p className="text-lg font-semibold">{result.risk_score}/100</p>
                </div>
                <div>
                  <span className="text-sm text-gray-500">Content Type</span>
                  <p className="text-sm font-medium capitalize">{result.content_type}</p>
                </div>
                <div>
                  <span className="text-sm text-gray-500">Confidence</span>
                  <p className="text-sm font-medium">{result.confidence_score}%</p>
                </div>
              </div>

              {result.issues_found.length > 0 && (
                <div className="mb-4">
                  <span className="text-sm font-medium text-gray-700">Issues Detected:</span>
                  <ul className="mt-1 list-disc list-inside text-sm text-gray-600">
                    {result.issues_found.map((issue, idx) => (
                      <li key={idx}>{issue}</li>
                    ))}
                  </ul>
                </div>
              )}

              {result.recommendations.length > 0 && (
                <div>
                  <span className="text-sm font-medium text-gray-700">Recommendations:</span>
                  <ul className="mt-1 list-disc list-inside text-sm text-gray-600">
                    {result.recommendations.map((rec, idx) => (
                      <li key={idx}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ResultsPanel;
