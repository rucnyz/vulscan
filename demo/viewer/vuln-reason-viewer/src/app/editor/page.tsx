// app/editor/page.tsx
"use client";

import { useState, useEffect, useMemo } from "react";
import { ResultData } from "@/lib/types";
import SearchBar from "@/components/SearchBar";
import PaginationControls from "@/components/PaginationControls";
import TaskInfoCard from "@/components/TaskInfoCard";
import ResultSampleCard from "@/components/ResultSampleCard";
import FileSelector from "@/components/FileSelector";
import Link from "next/link";

export default function EditorPage() {
  const [resultData, setResultData] = useState<ResultData | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(0);
  const [itemsPerPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // New state for file selection
  const [availableFiles, setAvailableFiles] = useState<string[]>([]);
  const [currentFile, setCurrentFile] = useState<string>("example.json");

  // Load available files
  useEffect(() => {
    async function loadFileList() {
      try {
        const response = await fetch("/api/files");
        const data = await response.json();

        if (data.files && Array.isArray(data.files) && data.files.length > 0) {
          setAvailableFiles(data.files);
          setCurrentFile(data.files[0]); // Set the first file as default
        }
      } catch (err) {
        console.error("Failed to load file list:", err);
        setError("Failed to load available files");
      }
    }

    loadFileList();
  }, []);

  // Load result data when file changes
  useEffect(() => {
    async function loadData() {
      try {
        setIsLoading(true);
        setError(null);

        const response = await fetch(
          `/api/results?file=${encodeURIComponent(currentFile)}`
        );

        if (!response.ok) {
          throw new Error(
            `Failed to load data: ${response.status} ${response.statusText}`
          );
        }

        const data = await response.json();
        setResultData(data);
      } catch (err) {
        console.error("Failed to load data:", err);
        setError(`Failed to load data from ${currentFile}`);
      } finally {
        setIsLoading(false);
      }
    }

    if (currentFile) {
      loadData();
    }
  }, [currentFile]);

  // Handle file change
  const handleFileChange = (filename: string) => {
    setCurrentFile(filename);
    setCurrentPage(0); // Reset to first page when changing file
    setSearchTerm(""); // Clear search when changing file
  };
  // Filter results based on search term
  const filteredResults = useMemo(() => {
    if (!resultData) return [];

    if (!searchTerm) return resultData.results;

    return resultData.results.filter((result) => {
      const searchLower = searchTerm.toLowerCase();
      return (
        result.input.toLowerCase().includes(searchLower) ||
        result.code.toLowerCase().includes(searchLower) ||
        result.output.toLowerCase().includes(searchLower) ||
        result.vuln_type.toLowerCase().includes(searchLower) ||
        result.pred_vuln_type?.toLowerCase().includes(searchLower) ||
        ("judge:" + result.judge).toLowerCase().includes(searchLower) || 
        ("idx:" + result.idx).toLowerCase().includes(searchLower)
      );
    });
  }, [resultData, searchTerm]);

  // Calculate pagination
  const totalPages = Math.ceil(filteredResults.length / itemsPerPage);
  const currentResults = filteredResults.slice(
    currentPage * itemsPerPage,
    (currentPage + 1) * itemsPerPage
  );

  // Handle page change
  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
  };

  // Handle search
  const handleSearch = (term: string) => {
    setSearchTerm(term);
    setCurrentPage(0); // Reset to first page when searching
  };

  if (isLoading && !resultData)
    return <div className="p-8 text-center">Loading...</div>;
  if (error && !resultData)
    return <div className="p-8 text-center text-red-500">{error}</div>;

  return (
    <div className="container mx-auto p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Vulnerability Results Editor</h1>
        
        <Link 
          href="/training" 
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
        >
          Switch to Training Data
        </Link>
      </div>

      {/* File selector */}
      {availableFiles.length > 0 && (
        <FileSelector
          files={availableFiles}
          currentFile={currentFile}
          onFileChange={handleFileChange}
        />
      )}

      <SearchBar searchTerm={searchTerm} onSearch={handleSearch} />

      {isLoading ? (
        <div className="p-8 text-center">Loading data...</div>
      ) : (
        <>
          {resultData && (
            <TaskInfoCard
              model={resultData.model}
              task={resultData.task}
              metrics={resultData.metrics}
            />
          )}
          <div className="mt-4 mb-6">
            <PaginationControls
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={handlePageChange}
              totalItems={filteredResults.length}
            />
          </div>

          {error && (
            <div className="p-4 mb-4 bg-red-100 text-red-700 rounded-lg">
              {error}
            </div>
          )}

          {currentResults.length > 0 ? (
            currentResults.map((result, index) => (
              <ResultSampleCard key={index} result={result} />
            ))
          ) : (
            <div className="p-8 text-center bg-gray-100 rounded-lg">
              {resultData
                ? "No results match your search criteria"
                : "No data available"}
            </div>
          )}
        </>
      )}
    </div>
  );
}
