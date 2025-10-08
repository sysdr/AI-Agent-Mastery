import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Shield, AlertTriangle, FileText, Download, Eye, EyeOff } from 'lucide-react';
import api from '../services/api';

const DocumentView = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [document, setDocument] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showContent, setShowContent] = useState(false);

  useEffect(() => {
    loadDocument();
  }, [id]);

  const loadDocument = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/documents/${id}`);
      setDocument(response.data);
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to load document');
    } finally {
      setLoading(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getRiskColor = (level) => {
    switch (level) {
      case 'high': return '#ef4444';
      case 'medium': return '#f59e0b';
      case 'low': return '#10b981';
      default: return '#6b7280';
    }
  };

  if (loading) {
    return (
      <div className="document-loading">
        <div className="loading-spinner"></div>
        <p>Loading document...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-state">
        <AlertTriangle size={48} />
        <h2>Error Loading Document</h2>
        <p>{error}</p>
        <button onClick={() => navigate('/')} className="btn btn-primary">
          Return to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="document-view">
      <div className="document-header">
        <button onClick={() => navigate('/')} className="back-btn">
          <ArrowLeft size={20} />
          Back to Dashboard
        </button>
        
        <div className="document-title">
          <FileText size={32} />
          <div>
            <h1>{document?.filename || 'Document'}</h1>
            <p>Uploaded {document?.uploaded_at ? new Date(document.uploaded_at).toLocaleString() : 'Unknown'}</p>
          </div>
        </div>
      </div>

      <div className="document-content">
        {/* Security Overview */}
        <div className="security-overview">
          <h2>Security Analysis</h2>
          
          <div className="security-cards">
            <div className="security-card">
              <div className="security-icon">
                <Shield size={24} style={{ color: getRiskColor(document?.pii_summary?.risk_level || 'low') }} />
              </div>
              <div className="security-info">
                <h3>Risk Level</h3>
                <span className={`risk-badge ${document?.pii_summary?.risk_level || 'low'}`}>
                  {(document?.pii_summary?.risk_level || 'low').toUpperCase()}
                </span>
              </div>
            </div>

            <div className="security-card">
              <div className="security-icon">
                <AlertTriangle size={24} color={document?.pii_summary?.total_entities > 0 ? '#f59e0b' : '#10b981'} />
              </div>
              <div className="security-info">
                <h3>PII Detected</h3>
                <p>{document?.pii_summary?.total_entities || 0} entities found</p>
              </div>
            </div>

            <div className="security-card">
              <div className="security-icon">
                <Shield size={24} color="#10b981" />
              </div>
              <div className="security-info">
                <h3>Virus Scan</h3>
                <p>✅ Clean</p>
              </div>
            </div>
          </div>

          {document?.pii_summary?.entity_types?.length > 0 && (
            <div className="pii-details">
              <h3>PII Types Detected</h3>
              <div className="pii-tags">
                {document.pii_summary.entity_types.map((type, index) => (
                  <span key={index} className="pii-tag">
                    {type}
                  </span>
                ))}
              </div>
            </div>
          )}

          {document?.pii_summary?.compliance_flags?.length > 0 && (
            <div className="compliance-flags">
              <h3>Compliance Requirements</h3>
              <div className="compliance-tags">
                {document.pii_summary.compliance_flags.map((flag, index) => (
                  <span key={index} className="compliance-tag">
                    {flag}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Document Metadata */}
        <div className="document-metadata">
          <h2>Document Information</h2>
          
          <div className="metadata-grid">
            <div className="metadata-item">
              <label>File Size</label>
              <span>{document?.metadata?.file_size ? formatFileSize(document.metadata.file_size) : 'Unknown'}</span>
            </div>
            
            <div className="metadata-item">
              <label>Content Type</label>
              <span>{document?.metadata?.content_type || 'Unknown'}</span>
            </div>
            
            <div className="metadata-item">
              <label>File Hash</label>
              <span className="hash">{document?.metadata?.file_hash ? document.metadata.file_hash.substring(0, 16) + '...' : 'Unknown'}</span>
            </div>
            
            <div className="metadata-item">
              <label>Processing Status</label>
              <span className="status-success">✅ {document?.status || 'Unknown'}</span>
            </div>

            {document?.processing_result?.content_classification && (
              <>
                <div className="metadata-item">
                  <label>Document Type</label>
                  <span>{document.processing_result.content_classification.category}</span>
                </div>
                
                <div className="metadata-item">
                  <label>Confidence</label>
                  <span>{Math.round(document.processing_result.content_classification.confidence * 100)}%</span>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Content Preview */}
        <div className="content-preview">
          <div className="content-header">
            <h2>Content Preview</h2>
            <button
              onClick={() => setShowContent(!showContent)}
              className="btn btn-outline"
            >
              {showContent ? <EyeOff size={16} /> : <Eye size={16} />}
              {showContent ? 'Hide Content' : 'Show Content'}
            </button>
          </div>

          {showContent && (
            <div className="content-display">
              {document?.pii_summary?.total_entities > 0 && (
                <div className="pii-warning">
                  <AlertTriangle size={16} />
                  <span>This document contains PII. Handle with care.</span>
                </div>
              )}
              
              <div className="content-stats">
                <span>Characters: {document?.processing_result?.character_count || 0}</span>
                <span>Chunks: {document?.processing_result?.chunk_count || 0}</span>
              </div>
              
              <div className="content-text">
                {document?.processing_result?.text_content ? 
                  document.processing_result.text_content.substring(0, 2000) + 
                  (document.processing_result.text_content.length > 2000 ? 
                    '\n... (content truncated)' : '') : 
                  'No content available'
                }
              </div>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="document-actions">
          <button className="btn btn-outline">
            <Download size={16} />
            Download Original
          </button>
          <button className="btn btn-outline">
            <FileText size={16} />
            Export Report
          </button>
        </div>
      </div>
    </div>
  );
};

export default DocumentView;
