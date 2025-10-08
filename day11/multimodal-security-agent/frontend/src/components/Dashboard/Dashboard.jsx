import React, { useState, useCallback } from 'react';
import { Upload, Shield, AlertTriangle, CheckCircle, FileText, Image, Headphones } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';
import axios from 'axios';
import ResultsPanel from '../Results/ResultsPanel';
import UploadZone from '../Upload/UploadZone';

const Dashboard = () => {
  const [analysisResults, setAnalysisResults] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [stats, setStats] = useState({
    totalFiles: 0,
    highRisk: 0,
    mediumRisk: 0,
    lowRisk: 0
  });

  const analyzeFile = async (file) => {
    setIsAnalyzing(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      let endpoint = '/api/analyze/';
      
      // Determine endpoint based on file type
      if (file.type.startsWith('image/')) {
        endpoint += 'image';
      } else if (file.type.startsWith('audio/')) {
        endpoint += 'audio';
      } else {
        endpoint += 'document';
      }

      const response = await axios.post(`http://localhost:8000${endpoint}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const result = response.data;
      setAnalysisResults(prev => [result, ...prev]);
      
      // Update stats
      setStats(prev => ({
        ...prev,
        totalFiles: prev.totalFiles + 1,
        [result.threat_level.toLowerCase() + 'Risk']: prev[result.threat_level.toLowerCase() + 'Risk'] + 1
      }));

      // Show notification
      const riskColor = {
        LOW: 'success',
        MEDIUM: 'warning', 
        HIGH: 'error',
        CRITICAL: 'error'
      };
      
      toast[riskColor[result.threat_level] || 'success'](
        `Analysis complete: ${result.threat_level} risk detected`
      );

    } catch (error) {
      console.error('Analysis failed:', error);
      toast.error('Analysis failed. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getThreatLevelColor = (level) => {
    const colors = {
      LOW: 'text-green-600 bg-green-100',
      MEDIUM: 'text-yellow-600 bg-yellow-100',
      HIGH: 'text-red-600 bg-red-100',
      CRITICAL: 'text-red-800 bg-red-200'
    };
    return colors[level] || 'text-gray-600 bg-gray-100';
  };

  const getThreatIcon = (level) => {
    switch(level) {
      case 'LOW':
        return <CheckCircle className="w-5 h-5" />;
      case 'MEDIUM':
        return <AlertTriangle className="w-5 h-5" />;
      case 'HIGH':
      case 'CRITICAL':
        return <AlertTriangle className="w-5 h-5" />;
      default:
        return <Shield className="w-5 h-5" />;
    }
  };

  const getContentTypeIcon = (type) => {
    switch(type) {
      case 'image':
        return <Image className="w-5 h-5" />;
      case 'document':
        return <FileText className="w-5 h-5" />;
      case 'audio':
        return <Headphones className="w-5 h-5" />;
      default:
        return <FileText className="w-5 h-5" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <Shield className="w-8 h-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">Multi-Modal Security Agent</h1>
            </div>
            <div className="text-sm text-gray-500">
              AI-Powered Content Moderation System
            </div>
          </div>
        </div>
      </header>

      {/* Stats Dashboard */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="flex items-center">
              <FileText className="w-8 h-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm text-gray-500">Total Files</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.totalFiles}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="flex items-center">
              <CheckCircle className="w-8 h-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm text-gray-500">Low Risk</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.lowRisk}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="flex items-center">
              <AlertTriangle className="w-8 h-8 text-yellow-600" />
              <div className="ml-4">
                <p className="text-sm text-gray-500">Medium Risk</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.mediumRisk}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="flex items-center">
              <AlertTriangle className="w-8 h-8 text-red-600" />
              <div className="ml-4">
                <p className="text-sm text-gray-500">High Risk</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.highRisk}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Upload Zone */}
        <div className="mb-8">
          <UploadZone onFileUpload={analyzeFile} isAnalyzing={isAnalyzing} />
        </div>

        {/* Results Panel */}
        {analysisResults.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm">
            <div className="px-6 py-4 border-b">
              <h2 className="text-lg font-semibold text-gray-900">Analysis Results</h2>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {analysisResults.map((result, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        {getContentTypeIcon(result.content_type)}
                        <span className="font-medium text-gray-900">{result.filename}</span>
                      </div>
                      <div className={`flex items-center space-x-2 px-3 py-1 rounded-full ${getThreatLevelColor(result.threat_level)}`}>
                        {getThreatIcon(result.threat_level)}
                        <span className="text-sm font-medium">{result.threat_level}</span>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                      <div>
                        <span className="text-sm text-gray-500">Risk Score</span>
                        <div className="flex items-center mt-1">
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full ${result.risk_score > 70 ? 'bg-red-600' : result.risk_score > 40 ? 'bg-yellow-600' : 'bg-green-600'}`}
                              style={{ width: `${result.risk_score}%` }}
                            ></div>
                          </div>
                          <span className="ml-2 text-sm font-medium">{result.risk_score}/100</span>
                        </div>
                      </div>
                      
                      <div>
                        <span className="text-sm text-gray-500">Confidence</span>
                        <p className="text-sm font-medium mt-1">{result.confidence_score}%</p>
                      </div>
                      
                      <div>
                        <span className="text-sm text-gray-500">Content Type</span>
                        <p className="text-sm font-medium mt-1 capitalize">{result.content_type}</p>
                      </div>
                    </div>

                    {result.issues_found.length > 0 && (
                      <div className="mb-3">
                        <span className="text-sm text-gray-500">Issues Found</span>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {result.issues_found.map((issue, idx) => (
                            <span key={idx} className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">
                              {issue}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {result.recommendations.length > 0 && (
                      <div>
                        <span className="text-sm text-gray-500">Recommendations</span>
                        <ul className="mt-1 text-sm text-gray-700">
                          {result.recommendations.map((rec, idx) => (
                            <li key={idx} className="flex items-start space-x-2">
                              <span className="text-blue-600">•</span>
                              <span>{rec}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
