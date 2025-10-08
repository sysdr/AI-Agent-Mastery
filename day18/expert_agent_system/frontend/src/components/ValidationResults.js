import React from 'react';
import { CheckCircle, AlertTriangle, XCircle, Clock, ExternalLink } from 'lucide-react';

const ValidationResults = ({ result }) => {
  const getConfidenceColor = (score) => {
    if (score >= 0.8) return 'text-green-600 bg-green-50';
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getExpertiseIcon = (level) => {
    switch (level) {
      case 'specialist':
      case 'expert':
        return <CheckCircle className="text-green-600" size={20} />;
      case 'intermediate':
        return <AlertTriangle className="text-yellow-600" size={20} />;
      default:
        return <XCircle className="text-red-600" size={20} />;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-semibold mb-4">Validation Results</h2>
      
      {/* Response */}
      <div className="mb-6">
        <h3 className="text-lg font-medium mb-2">Expert Response</h3>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-gray-800">{result.response}</p>
        </div>
      </div>

      {/* Confidence and Expertise */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">Confidence Score</span>
            <div className={`px-2 py-1 rounded text-sm font-semibold ${getConfidenceColor(result.confidence_score)}`}>
              {(result.confidence_score * 100).toFixed(1)}%
            </div>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full ${
                result.confidence_score >= 0.8 ? 'bg-green-600' :
                result.confidence_score >= 0.6 ? 'bg-yellow-600' : 'bg-red-600'
              }`}
              style={{ width: `${result.confidence_score * 100}%` }}
            ></div>
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-600">Expertise Level</span>
            {getExpertiseIcon(result.expertise_level)}
          </div>
          <div className="capitalize text-lg font-semibold text-gray-800 mt-1">
            {result.expertise_level}
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-600">Processing Time</span>
            <Clock className="text-gray-600" size={20} />
          </div>
          <div className="text-lg font-semibold text-gray-800 mt-1">
            {result.processing_time?.toFixed(2)}s
          </div>
        </div>
      </div>

      {/* Escalation Warning */}
      {result.escalation_required && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="flex items-center">
            <AlertTriangle className="text-red-600 mr-2" size={20} />
            <span className="text-red-800 font-medium">
              Human Expert Review Required
            </span>
          </div>
          <p className="text-red-700 text-sm mt-1">
            Confidence below required threshold. Consider consulting a human expert.
          </p>
        </div>
      )}

      {/* Sources */}
      {result.sources_validated && result.sources_validated.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-medium mb-2">Validated Sources</h3>
          <div className="space-y-2">
            {result.sources_validated.map((source, index) => (
              <div key={index} className="bg-gray-50 rounded-lg p-3 flex items-center justify-between">
                <span className="text-sm text-gray-700 truncate flex-1">{source}</span>
                {source.startsWith('http') && (
                  <ExternalLink className="text-gray-500 ml-2" size={16} />
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Explanation */}
      <div>
        <h3 className="text-lg font-medium mb-2">Validation Explanation</h3>
        <div className="bg-blue-50 rounded-lg p-4">
          <p className="text-blue-800 text-sm">{result.explanation}</p>
        </div>
      </div>
    </div>
  );
};

export default ValidationResults;
