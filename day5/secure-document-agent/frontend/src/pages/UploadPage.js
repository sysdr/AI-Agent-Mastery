import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, AlertCircle, CheckCircle, X } from 'lucide-react';
import api from '../services/api';

const UploadPage = () => {
  const [dragActive, setDragActive] = useState(false);
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadResults, setUploadResults] = useState([]);
  const navigate = useNavigate();

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files);
    }
  };

  const handleFiles = (fileList) => {
    const newFiles = Array.from(fileList).map(file => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      status: 'pending'
    }));
    setFiles(prev => [...prev, ...newFiles]);
  };

  const removeFile = (fileId) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const uploadFiles = async () => {
    if (files.length === 0) return;

    setUploading(true);
    const results = [];

    for (const fileItem of files) {
      try {
        const formData = new FormData();
        formData.append('file', fileItem.file);

        const response = await api.post('/documents/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        results.push({
          ...fileItem,
          status: 'success',
          result: response.data
        });

      } catch (error) {
        results.push({
          ...fileItem,
          status: 'error',
          error: error.response?.data?.detail || 'Upload failed'
        });
      }
    }

    setUploadResults(results);
    setUploading(false);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="upload-page">
      <div className="upload-header">
        <h1>Upload Documents</h1>
        <p>Securely upload and process documents with automatic PII detection and malware scanning</p>
      </div>

      {!uploading && uploadResults.length === 0 && (
        <>
          {/* Upload Zone */}
          <div 
            className={`upload-zone ${dragActive ? 'drag-active' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <div className="upload-content">
              <Upload size={48} />
              <h3>Drag and drop files here</h3>
              <p>or click to select files</p>
              <input
                type="file"
                multiple
                onChange={handleChange}
                className="file-input"
                accept=".pdf,.docx,.txt,.xlsx,.png,.jpg,.jpeg"
              />
            </div>
          </div>

          {/* File List */}
          {files.length > 0 && (
            <div className="file-list">
              <h3>Selected Files ({files.length})</h3>
              {files.map(fileItem => (
                <div key={fileItem.id} className="file-item">
                  <FileText size={24} />
                  <div className="file-info">
                    <h4>{fileItem.file.name}</h4>
                    <p>{formatFileSize(fileItem.file.size)}</p>
                  </div>
                  <button
                    onClick={() => removeFile(fileItem.id)}
                    className="remove-btn"
                  >
                    <X size={20} />
                  </button>
                </div>
              ))}
              
              <div className="upload-actions">
                <button
                  onClick={uploadFiles}
                  className="btn btn-primary"
                  disabled={files.length === 0}
                >
                  Upload {files.length} File{files.length !== 1 ? 's' : ''}
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {/* Upload Progress */}
      {uploading && (
        <div className="upload-progress">
          <div className="progress-header">
            <h3>Processing Files...</h3>
            <div className="loading-spinner"></div>
          </div>
          <p>Scanning for malware, detecting PII, and extracting content...</p>
        </div>
      )}

      {/* Upload Results */}
      {uploadResults.length > 0 && (
        <div className="upload-results">
          <h3>Upload Results</h3>
          {uploadResults.map(result => (
            <div key={result.id} className={`result-item ${result.status}`}>
              <div className="result-icon">
                {result.status === 'success' ? 
                  <CheckCircle size={24} /> : 
                  <AlertCircle size={24} />
                }
              </div>
              
              <div className="result-content">
                <h4>{result.file.name}</h4>
                
                {result.status === 'success' ? (
                  <div className="success-details">
                    <p>✅ Document processed successfully</p>
                    {result.result.pii_summary.total_entities > 0 && (
                      <div className="pii-warning">
                        <AlertCircle size={16} />
                        <span>PII detected: {result.result.pii_summary.entity_types.join(', ')}</span>
                      </div>
                    )}
                    <button
                      onClick={() => navigate(`/document/${result.result.document_id}`)}
                      className="btn btn-sm btn-outline"
                    >
                      View Document
                    </button>
                  </div>
                ) : (
                  <div className="error-details">
                    <p>❌ {result.error}</p>
                  </div>
                )}
              </div>
            </div>
          ))}
          
          <div className="results-actions">
            <button
              onClick={() => navigate('/')}
              className="btn btn-primary"
            >
              Go to Dashboard
            </button>
            <button
              onClick={() => {
                setFiles([]);
                setUploadResults([]);
              }}
              className="btn btn-outline"
            >
              Upload More Files
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadPage;
