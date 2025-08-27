// components/FileSelector.tsx
'use client';

import { useState } from 'react';

interface FileSelectorProps {
  files: string[];
  currentFile: string;
  onFileChange: (file: string) => void;
}

export default function FileSelector({ files, currentFile, onFileChange }: FileSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);

  // Toggle dropdown
  const toggleDropdown = () => setIsOpen(!isOpen);

  // Handle file selection
  const handleFileSelect = (file: string) => {
    onFileChange(file);
    setIsOpen(false);
  };

  return (
    <div className="relative mb-4">
      <div className="flex items-center">
        <label className="mr-2 font-medium">Select File:</label>
        <div className="relative inline-block text-left">
          <button 
            onClick={toggleDropdown}
            type="button"
            className="inline-flex justify-between items-center w-full rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            id="file-menu"
            aria-expanded="true"
            aria-haspopup="true"
          >
            {currentFile}
            <svg className="-mr-1 ml-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>

          {isOpen && (
            <div 
              className="origin-top-right absolute right-0 mt-2 w-full rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-10"
              role="menu"
              aria-orientation="vertical"
              aria-labelledby="file-menu"
            >
              <div className="py-1 max-h-60 overflow-y-auto" role="none">
                {files.map((file) => (
                  <button
                    key={file}
                    onClick={() => handleFileSelect(file)}
                    className={`${
                      file === currentFile ? 'bg-gray-100 text-gray-900' : 'text-gray-700'
                    } block w-full text-left px-4 py-2 text-sm hover:bg-gray-100`}
                    role="menuitem"
                  >
                    {file}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}