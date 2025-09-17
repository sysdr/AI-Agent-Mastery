import React from 'react';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';

function FileUpload({ onFileUpload }) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif'],
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxSize: 10485760, // 10MB
    onDrop: (acceptedFiles, rejectedFiles) => {
      if (rejectedFiles.length > 0) {
        toast.error('File rejected. Please check file type and size.');
        return;
      }
      
      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0];
        const message = prompt('Add a message about this file (optional):');
        onFileUpload(file, message || '');
      }
    }
  });

  return (
    <div {...getRootProps()} className={`file-upload-area ${isDragActive ? 'active' : ''}`}>
      <input {...getInputProps()} />
      <span className="upload-icon">📎</span>
      <span className="upload-text">
        {isDragActive ? 'Drop file here' : 'Attach file'}
      </span>
    </div>
  );
}

export default FileUpload;
