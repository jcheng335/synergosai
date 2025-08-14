import React, { useState } from 'react';
import { Upload, FileText, Link, CheckCircle, AlertCircle, Loader2, ArrowRight } from 'lucide-react';

const DocumentUpload = ({ interview, onDocumentsUploaded }) => {
  const interviewId = interview?.id;
  const [uploadStatus, setUploadStatus] = useState({});
  const [urlInputs, setUrlInputs] = useState({});
  const [activeTab, setActiveTab] = useState({ job_listing: 'file' }); // Default to file upload
  const [selectedFiles, setSelectedFiles] = useState({});

  const documentTypes = [
    {
      key: 'resume',
      title: 'Candidate Resume',
      description: 'Upload the candidate\'s resume or CV',
      required: true,
      icon: FileText,
      acceptedFormats: 'PDF,DOC,DOCX,TXT'
    },
    {
      key: 'job_listing',
      title: 'Job Listing',
      description: 'Upload the job description and requirements',
      required: true,
      icon: FileText,
      acceptedFormats: 'PDF,DOC,DOCX,TXT',
      hasUrlOption: true
    },
    {
      key: 'questions',
      title: 'Company Questions',
      description: 'Upload company-specific interview questions (optional)',
      required: false,
      icon: FileText,
      acceptedFormats: 'PDF,DOC,DOCX,TXT'
    }
  ];

  const convertFileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result);
      reader.onerror = error => reject(error);
    });
  };

  const handleFileUpload = async (file, documentType) => {
    if (!file) return;

    // Validate file type
    const allowedTypes = ['text/plain', 'application/pdf', 'application/msword', 
                         'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    const allowedExtensions = ['.txt', '.pdf', '.doc', '.docx'];
    
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
      setUploadStatus(prev => ({
        ...prev,
        [documentType]: { status: 'error', message: 'Invalid file type. Please upload PDF, DOC, DOCX, or TXT files.' }
      }));
      return;
    }

    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      setUploadStatus(prev => ({
        ...prev,
        [documentType]: { status: 'error', message: 'File size must be less than 10MB.' }
      }));
      return;
    }

    setUploadStatus(prev => ({
      ...prev,
      [documentType]: { status: 'uploading', message: 'Converting and uploading file...' }
    }));

    try {
      // Convert file to base64
      const base64Data = await convertFileToBase64(file);
      
      // Upload using base64 API
      const response = await fetch(`http://localhost:5001/api/interviews/${interviewId}/documents-base64`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          file_data: base64Data,
          filename: file.name,
          document_type: documentType
        })
      });

      const result = await response.json();

      if (response.ok) {
        setUploadStatus(prev => ({
          ...prev,
          [documentType]: { 
            status: 'success', 
            message: 'File uploaded successfully!',
            document: result.document
          }
        }));
        
        // Don't call onDocumentsUploaded here - wait for the Analyze button
        // if (onDocumentsUploaded) {
        //   onDocumentsUploaded(documentType, result.document);
        // }
      } else {
        throw new Error(result.error || 'Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus(prev => ({
        ...prev,
        [documentType]: { 
          status: 'error', 
          message: error.message || 'Upload failed. Please try again.' 
        }
      }));
    }
  };

  const handleUrlSubmit = async (documentType) => {
    const url = urlInputs[documentType];
    if (!url) return;

    // Basic URL validation
    try {
      new URL(url);
    } catch {
      setUploadStatus(prev => ({
        ...prev,
        [documentType]: { status: 'error', message: 'Please enter a valid URL.' }
      }));
      return;
    }

    setUploadStatus(prev => ({
      ...prev,
      [documentType]: { status: 'uploading', message: 'Processing URL...' }
    }));

    try {
      const response = await fetch(`http://localhost:5001/api/interviews/${interviewId}/job-url-enhanced`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url })
      });

      const result = await response.json();

      if (response.ok) {
        setUploadStatus(prev => ({
          ...prev,
          [documentType]: { 
            status: 'success', 
            message: 'URL processed successfully!',
            document: result.document
          }
        }));
        
        // Don't call onDocumentsUploaded here - wait for the Analyze button
        // if (onDocumentsUploaded) {
        //   onDocumentsUploaded(documentType, result.document);
        // }
      } else {
        throw new Error(result.error || 'URL processing failed');
      }
    } catch (error) {
      console.error('URL processing error:', error);
      setUploadStatus(prev => ({
        ...prev,
        [documentType]: { 
          status: 'error', 
          message: error.message || 'URL processing failed. Please try again.' 
        }
      }));
    }
  };

  const handleFileInputChange = (event, documentType) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFiles(prev => ({ ...prev, [documentType]: file }));
      setUploadStatus(prev => ({
        ...prev,
        [documentType]: { status: 'ready', message: `Selected: ${file.name}` }
      }));
    }
  };

  const handleUploadClick = (documentType) => {
    const file = selectedFiles[documentType];
    if (file) {
      handleFileUpload(file, documentType);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'uploading':
        return <Loader2 className="w-4 h-4 animate-spin text-blue-500" />;
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'uploading':
        return 'text-blue-600';
      case 'success':
        return 'text-green-600';
      case 'error':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload Documents</h2>
        <p className="text-gray-600">
          Upload the necessary documents to begin AI analysis and question generation.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {documentTypes.map((docType) => {
          const status = uploadStatus[docType.key];
          const IconComponent = docType.icon;

          return (
            <div key={docType.key} className="border border-gray-200 rounded-lg p-6">
              <div className="flex items-center mb-4">
                <IconComponent className="w-6 h-6 text-blue-600 mr-3" />
                <div>
                  <h3 className="font-semibold text-gray-900">
                    {docType.title}
                    {docType.required && <span className="text-red-500 ml-1">*</span>}
                  </h3>
                  <p className="text-sm text-gray-600">{docType.description}</p>
                </div>
              </div>

              {/* Tab navigation for job listing */}
              {docType.hasUrlOption && (
                <div className="flex mb-4 border-b border-gray-200">
                  <button
                    onClick={() => setActiveTab(prev => ({ ...prev, [docType.key]: 'file' }))}
                    className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                      activeTab[docType.key] === 'file'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    <Upload className="w-4 h-4 inline mr-2" />
                    Upload File
                  </button>
                  <button
                    onClick={() => setActiveTab(prev => ({ ...prev, [docType.key]: 'url' }))}
                    className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                      activeTab[docType.key] === 'url'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    <Link className="w-4 h-4 inline mr-2" />
                    Enter URL
                  </button>
                </div>
              )}

              {/* File upload section */}
              {(!docType.hasUrlOption || activeTab[docType.key] === 'file') && (
                <div className="space-y-3">
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
                    <input
                      type="file"
                      id={`file-${docType.key}`}
                      className="hidden"
                      accept=".pdf,.doc,.docx,.txt"
                      onChange={(e) => handleFileInputChange(e, docType.key)}
                      disabled={status?.status === 'uploading'}
                    />
                    <label
                      htmlFor={`file-${docType.key}`}
                      className="cursor-pointer flex flex-col items-center"
                    >
                      <Upload className="w-8 h-8 text-gray-400 mb-2" />
                      <span className="text-sm font-medium text-gray-900">
                        Click to select file
                      </span>
                      <span className="text-xs text-gray-500 mt-1">
                        {docType.acceptedFormats}
                      </span>
                    </label>
                  </div>
                  {selectedFiles[docType.key] && status?.status === 'ready' && (
                    <button
                      onClick={() => handleUploadClick(docType.key)}
                      className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                      disabled={status?.status === 'uploading'}
                    >
                      Upload {selectedFiles[docType.key].name}
                    </button>
                  )}
                </div>
              )}

              {/* URL input section */}
              {docType.hasUrlOption && activeTab[docType.key] === 'url' && (
                <div className="space-y-3">
                  <div className="flex space-x-2">
                    <input
                      type="url"
                      placeholder="https://example.com/job-posting"
                      value={urlInputs[docType.key] || ''}
                      onChange={(e) => setUrlInputs(prev => ({ ...prev, [docType.key]: e.target.value }))}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      disabled={status?.status === 'uploading'}
                    />
                    <button
                      onClick={() => handleUrlSubmit(docType.key)}
                      disabled={!urlInputs[docType.key] || status?.status === 'uploading'}
                      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                    >
                      {status?.status === 'uploading' ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <>
                          <Link className="w-4 h-4 mr-2" />
                          Add URL
                        </>
                      )}
                    </button>
                  </div>
                  <p className="text-xs text-gray-500">
                    Enter the URL of the job posting to automatically extract job details
                  </p>
                </div>
              )}

              {/* Status display */}
              {status && (
                <div className={`mt-3 flex items-center text-sm ${getStatusColor(status.status)}`}>
                  {getStatusIcon(status.status)}
                  <span className="ml-2">{status.message}</span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Ready to analyze section */}
      <div className="bg-gray-50 rounded-lg p-6">
        <div className="flex items-center mb-2">
          <CheckCircle className="w-5 h-5 text-gray-400 mr-2" />
          <h3 className="font-semibold text-gray-900">Ready to Analyze?</h3>
        </div>
        <p className="text-gray-600 mb-4">
          Once you've uploaded the required documents, we'll analyze them to generate tailored interview questions.
        </p>
        
        {/* Check if required documents are uploaded */}
        {uploadStatus.resume?.status === 'success' && uploadStatus.job_listing?.status === 'success' ? (
          <button
            onClick={async () => {
              setUploadStatus(prev => ({
                ...prev,
                analyzing: { status: 'uploading', message: 'Analyzing documents and generating questions...' }
              }));
              
              try {
                // Trigger analysis
                const response = await fetch(`http://localhost:5001/api/interviews/${interviewId}/analyze`, {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                  }
                });
                
                if (response.ok) {
                  setUploadStatus(prev => ({
                    ...prev,
                    analyzing: { status: 'success', message: 'Analysis complete!' }
                  }));
                  setTimeout(() => onDocumentsUploaded(), 1000);
                } else {
                  throw new Error('Analysis failed');
                }
              } catch (error) {
                setUploadStatus(prev => ({
                  ...prev,
                  analyzing: { status: 'error', message: 'Analysis failed. Using default questions.' }
                }));
                // Continue anyway with default questions
                setTimeout(() => onDocumentsUploaded(), 2000);
              }
            }}
            disabled={uploadStatus.analyzing?.status === 'uploading'}
            className="px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 flex items-center disabled:opacity-50"
          >
            {uploadStatus.analyzing?.status === 'uploading' ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <span>Analyze & Continue</span>
                <ArrowRight className="w-4 h-4 ml-2" />
              </>
            )}
          </button>
        ) : (
          <div className="flex items-center text-amber-600 text-sm">
            <AlertCircle className="w-4 h-4 mr-2" />
            <span>Please upload resume and job listing to continue</span>
          </div>
        )}
        
        {/* Analysis status */}
        {uploadStatus.analyzing && (
          <div className={`mt-3 flex items-center text-sm ${getStatusColor(uploadStatus.analyzing.status)}`}>
            {getStatusIcon(uploadStatus.analyzing.status)}
            <span className="ml-2">{uploadStatus.analyzing.message}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentUpload;

