'use client';

import { useState, useEffect } from 'react';

interface FileItem {
  name: string;
  path: string;
  size: number;
  isDirectory: boolean;
  createdAt: string;
  modifiedAt: string;
}

export default function FileManager() {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch file list
  const fetchFiles = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/files/list');
      if (!response.ok) {
        throw new Error('Failed to fetch files');
      }
      const data = await response.json();
      setFiles(data.files);
      setError(null);
    } catch (err) {
      setError('Failed to load files');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Delete a file
  const deleteFile = async (filename: string) => {
    if (!confirm(`Are you sure you want to delete ${filename}?`)) {
      return;
    }

    try {
      const response = await fetch(`/api/files/delete?filename=${encodeURIComponent(filename)}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete file');
      }

      await fetchFiles(); // Refresh the list
    } catch (err) {
      setError('Failed to delete file');
      console.error(err);
    }
  };

  // Handle file upload
  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) {
      return;
    }

    const file = e.target.files[0];
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/files/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to upload file');
      }

      await fetchFiles(); // Refresh the list
    } catch (err) {
      setError('Failed to upload file');
      console.error(err);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">File Manager</h1>

      {/* Upload section */}
      <div className="mb-6 p-4 bg-white rounded shadow">
        <h2 className="text-xl font-semibold mb-2">Upload File</h2>
        <input 
          type="file" 
          onChange={handleUpload} 
          className="block w-full text-sm text-gray-500
            file:mr-4 file:py-2 file:px-4
            file:rounded-full file:border-0
            file:text-sm file:font-semibold
            file:bg-blue-50 file:text-blue-700
            hover:file:bg-blue-100"
        />
      </div>

      {/* File list */}
      <div className="bg-white rounded shadow overflow-hidden">
        <h2 className="text-xl font-semibold p-4 border-b">Files</h2>
        
        {loading ? (
          <div className="flex justify-center p-8">
            <p>Loading...</p>
          </div>
        ) : error ? (
          <div className="p-4 text-red-500">{error}</div>
        ) : files.length === 0 ? (
          <div className="p-8 text-center text-gray-500">No files found</div>
        ) : (
          <ul>
            {files.map((file) => (
              <li key={file.path} className="border-b last:border-b-0 hover:bg-gray-50">
                <div className="flex items-center justify-between p-4">
                  <div>
                    <p className="font-medium">{file.name}</p>
                    <p className="text-sm text-gray-500">
                      {file.isDirectory ? 'Directory' : `${(file.size / 1024).toFixed(2)} KB`}
                    </p>
                  </div>
                  <div className="flex space-x-2">
                    <button 
                      onClick={() => deleteFile(file.name)}
                      className="px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}