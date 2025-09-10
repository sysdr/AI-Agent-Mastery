import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, Image, Headphones, Loader } from 'lucide-react';

const UploadZone = ({ onFileUpload, isAnalyzing }) => {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      onFileUpload(acceptedFiles[0]);
    }
  }, [onFileUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'],
      'audio/*': ['.mp3', '.wav', '.ogg', '.m4a'],
      'text/plain': ['.txt'],
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    }
  });

  return (
    <div className="bg-white rounded-lg shadow-sm">
      <div className="px-6 py-4 border-b">
        <h2 className="text-lg font-semibold text-gray-900">Upload Content for Analysis</h2>
        <p className="text-sm text-gray-500 mt-1">
          Supports images, documents (PDF, DOC, TXT), and audio files
        </p>
      </div>
      
      <div className="p-6">
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-blue-400 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          } ${isAnalyzing ? 'pointer-events-none opacity-50' : ''}`}
        >
          <input {...getInputProps()} />
          
          <div className="flex flex-col items-center space-y-4">
            {isAnalyzing ? (
              <>
                <Loader className="w-12 h-12 text-blue-600 animate-spin" />
                <p className="text-lg text-gray-600">Analyzing content...</p>
                <p className="text-sm text-gray-500">
                  Running security checks and content moderation
                </p>
              </>
            ) : (
              <>
                <Upload className="w-12 h-12 text-gray-400" />
                
                {isDragActive ? (
                  <p className="text-lg text-blue-600">Drop the file here...</p>
                ) : (
                  <>
                    <p className="text-lg text-gray-600">
                      Drag & drop a file here, or click to select
                    </p>
                    <p className="text-sm text-gray-500">
                      Maximum file size: 50MB
                    </p>
                  </>
                )}
                
                <div className="flex items-center space-x-6 text-sm text-gray-500">
                  <div className="flex items-center space-x-2">
                    <Image className="w-4 h-4" />
                    <span>Images</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <FileText className="w-4 h-4" />
                    <span>Documents</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Headphones className="w-4 h-4" />
                    <span>Audio</span>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
        
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center space-x-3 p-4 bg-blue-50 rounded-lg">
            <Image className="w-6 h-6 text-blue-600" />
            <div>
              <p className="text-sm font-medium text-blue-900">Image Analysis</p>
              <p className="text-xs text-blue-700">Malware detection, content moderation</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3 p-4 bg-green-50 rounded-lg">
            <FileText className="w-6 h-6 text-green-600" />
            <div>
              <p className="text-sm font-medium text-green-900">Document Scanning</p>
              <p className="text-xs text-green-700">PII detection, content classification</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3 p-4 bg-purple-50 rounded-lg">
            <Headphones className="w-6 h-6 text-purple-600" />
            <div>
              <p className="text-sm font-medium text-purple-900">Audio Processing</p>
              <p className="text-xs text-purple-700">Speech recognition, content filtering</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadZone;
