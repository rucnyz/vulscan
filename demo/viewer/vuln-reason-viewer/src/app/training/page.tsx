"use client";

import React, { useState, useEffect, useMemo } from "react";
import SearchBar from "@/components/SearchBar";
import PaginationControls from "@/components/PaginationControls";
import FileSelector from "@/components/FileSelector";
import Link from "next/link";

// Define types for the conversation format
interface ConversationMessage {
  from: string;
  value: string;
}

interface ConversationItem {
  system: string;
  idx: number;
  cwe: (string | number)[];
  conversations: ConversationMessage[];
  ground_truth?: string;
}

export default function TrainingPage() {
  const [resultData, setResultData] = useState<ConversationItem[] | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(0);
  const [itemsPerPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 文件选择状态
  const [availableFiles, setAvailableFiles] = useState<string[]>([]);
  const [currentFile, setCurrentFile] = useState<string>("");
  const [directoryInfo, setDirectoryInfo] = useState<string>("");
  const [setupMessage, setSetupMessage] = useState<string>("");
  const [isDataSlicing, setIsDataSlicing] = useState(false);

  // 加载可用的训练数据文件
  useEffect(() => {
    async function loadFileList() {
      try {
        const response = await fetch("/api/training-files");
        const data = await response.json();

        if (data.message) {
          setSetupMessage(data.message);
        }

        if (data.directory) {
          setDirectoryInfo(data.directory);
        }

        if (data.files && Array.isArray(data.files)) {
          setAvailableFiles(data.files);
          if (data.files.length > 0) {
            setCurrentFile(data.files[0]); // 将第一个文件设置为默认值
          }
        }
      } catch (err) {
        console.error("Failed to load training file list:", err);
        setError("Failed to load available training files");
      }
    }

    loadFileList();
  }, []);

  // 当文件变更时加载结果数据
  useEffect(() => {
    async function loadData() {
      try {
        setIsLoading(true);
        setError(null);

        const response = await fetch(
          `/api/training-results?file=${encodeURIComponent(currentFile)}`
        );

        if (!response.ok) {
          throw new Error(
            `Failed to load training data: ${response.status} ${response.statusText}`
          );
        }

        // 优化大数据集加载
        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let partialData = '';
        
        if (reader) {
          try {
            // 显示正在解析的消息
            setResultData(null);
            setError("Parsing large JSON dataset... This may take a moment.");
            
            while (true) {
              const { done, value } = await reader.read();
              
              if (done) {
                break;
              }
              
              // 累积数据块
              partialData += decoder.decode(value, { stream: true });
            }
            
            // 完成所有数据的读取
            partialData += decoder.decode();
            
            try {
              const data = JSON.parse(partialData);
              setResultData(data);
              setError(null);
            } catch (jsonError: any) {
              console.error("Failed to parse JSON data:", jsonError);
              setError(`Failed to parse JSON data: ${jsonError.message}`);
            }
          } catch (streamError: any) {
            console.error("Error reading stream:", streamError);
            setError(`Error reading data stream: ${streamError.message}`);
          }
        } else {
          // 回退到普通JSON解析
          const data = await response.json();
          setResultData(data);
        }
      } catch (err) {
        console.error("Failed to load training data:", err);
        setError(`Failed to load training data from ${currentFile}`);
      } finally {
        setIsLoading(false);
      }
    }

    if (currentFile) {
      loadData();
    }
  }, [currentFile]);

  // 处理文件变更
  const handleFileChange = (filename: string) => {
    setCurrentFile(filename);
    setCurrentPage(0); // 切换文件时重置到第一页
    setSearchTerm(""); // 切换文件时清除搜索
  };

  // 基于搜索词过滤结果
  const filteredResults = useMemo(() => {
    if (!resultData || !Array.isArray(resultData)) return [];

    if (!searchTerm) return resultData;

    // 优化搜索：对话数据的搜索
    return resultData.filter((result) => {
      const searchLower = searchTerm.toLowerCase();
      
      // 在CWE中搜索
      if (result.cwe && Array.isArray(result.cwe) && 
          result.cwe.some((cwe: string | number) => String(cwe).toLowerCase().includes(searchLower))) {
        return true;
      }
      
      // 在对话内容中搜索
      if (result.conversations && Array.isArray(result.conversations)) {
        return result.conversations.some((msg: ConversationMessage) => 
          msg.value && msg.value.toLowerCase().includes(searchLower)
        );
      }
      
      // 系统消息搜索
      if (result.system && result.system.toLowerCase().includes(searchLower)) {
        return true;
      }
      
      // idx搜索
      if (result.idx && String(result.idx).includes(searchLower)) {
        return true;
      }
      
      return false;
    });
  }, [resultData, searchTerm]);

  // 改进后的分页计算 - 提高大数据集性能
  const totalPages = Math.ceil((filteredResults?.length || 0) / itemsPerPage);
  
  const currentResults = useMemo(() => {
    if (!filteredResults || filteredResults.length === 0) return [];
    
    // 对于大数据集，添加状态指示切片操作
    if (filteredResults.length > 1000) {
      setIsDataSlicing(true);
      // 使用setTimeout允许UI先更新，然后再进行大型数组切片
      setTimeout(() => setIsDataSlicing(false), 0);
    }
    
    return filteredResults.slice(
      currentPage * itemsPerPage,
      (currentPage + 1) * itemsPerPage
    );
  }, [filteredResults, currentPage, itemsPerPage]);

  // 处理页面变更
  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
  };

  // 处理搜索
  const handleSearch = (term: string) => {
    setSearchTerm(term);
    setCurrentPage(0); // 搜索时重置到第一页
  };

  // 添加一个辅助函数，用于格式化助手消息 - 只保留新的标签格式
  const formatAssistantMessage = (message: string) => {
    // 创建一个新的message副本以避免修改原始消息
    let processedMessage = message;
    
    // 只保留支持一种格式的标签（新格式）
    const thoughtStartTag = "<|begin_of_thought|>";
    const thoughtEndTag = "<|end_of_thought|>";
    
    // 支持解决方案部分
    const solutionStartTag = "<|begin_of_solution|>";
    const solutionEndTag = "<|end_of_solution|>";
    
    // 首先使用React Fragment收集所有处理过的内容部分
    const contentParts: React.JSX.Element[] = [];
    
    // 处理思考部分
    if (message.includes(thoughtStartTag) && message.includes(thoughtEndTag)) {
      const thoughtStart = message.indexOf(thoughtStartTag);
      const thoughtEnd = message.indexOf(thoughtEndTag) + thoughtEndTag.length;
      
      if (thoughtStart !== -1 && thoughtEnd !== -1) {
        // 添加思考前的内容
        const beforeThought = message.substring(0, thoughtStart);
        if (beforeThought) {
          contentParts.push(<div key="before-thought" className="mb-2">{beforeThought}</div>);
        }
        
        // 添加思考过程
        const thought = message.substring(
          thoughtStart + thoughtStartTag.length, 
          message.indexOf(thoughtEndTag)
        );
        contentParts.push(
          <div key="thought" className="mt-2 mb-2 p-3 bg-yellow-50 border-l-4 border-yellow-500 rounded">
            <div className="font-bold text-yellow-700 mb-1">Thought Process</div>
            <div className="whitespace-pre-wrap">{formatCodeBlocks(thought)}</div>
          </div>
        );
        
        // 更新消息为剩余部分以处理其他标签
        processedMessage = message.substring(thoughtEnd);
      }
    }
    
    // 处理解决方案部分
    if (processedMessage.includes(solutionStartTag) && processedMessage.includes(solutionEndTag)) {
      const solutionStart = processedMessage.indexOf(solutionStartTag);
      const solutionEnd = processedMessage.indexOf(solutionEndTag) + solutionEndTag.length;
      
      if (solutionStart !== -1 && solutionEnd !== -1) {
        // 添加解决方案前的内容
        const beforeSolution = processedMessage.substring(0, solutionStart);
        if (beforeSolution) {
          contentParts.push(<div key="before-solution" className="mb-2">{formatCodeBlocks(beforeSolution)}</div>);
        }
        
        // 添加解决方案
        const solution = processedMessage.substring(
          solutionStart + solutionStartTag.length, 
          processedMessage.indexOf(solutionEndTag)
        );
        contentParts.push(
          <div key="solution" className="mt-2 mb-2 p-3 bg-green-50 border-l-4 border-green-500 rounded">
            <div className="font-bold text-green-700 mb-1">Solution</div>
            <div className="whitespace-pre-wrap">{formatCodeBlocks(solution)}</div>
          </div>
        );
        
        // 添加解决方案后的内容
        const afterSolution = processedMessage.substring(solutionEnd);
        if (afterSolution) {
          contentParts.push(<div key="after-solution" className="mt-2">{formatCodeBlocks(afterSolution)}</div>);
        }
        
        // 所有内容都已处理
        return <>{contentParts}</>;
      }
    }
    
    // 如果到这里还有剩余内容，添加到结果中
    if (processedMessage && processedMessage !== message) {
      contentParts.push(<div key="remaining" className="whitespace-pre-wrap">{formatCodeBlocks(processedMessage)}</div>);
      return <>{contentParts}</>;
    }
    
    // 如果没有特殊标签或所有标签都已处理，返回原始消息
    return contentParts.length > 0 
      ? <>{contentParts}</> 
      : <div className="whitespace-pre-wrap">{formatCodeBlocks(message)}</div>;
  };

  // 添加一个辅助函数，用于格式化代码块
  const formatCodeBlocks = (text: string): React.JSX.Element => {
    // 检查文本中是否包含代码块（使用```标记的代码块）
    if (!text.includes("```")) {
      return <>{text}</>;
    }

    // 分割文本，处理代码块
    const parts: React.JSX.Element[] = [];
    let currentIndex = 0;
    let codeBlockStart = text.indexOf("```", currentIndex);
    
    while (codeBlockStart !== -1) {
      // 添加代码块前的文本
      if (codeBlockStart > currentIndex) {
        parts.push(
          <span key={`text-${currentIndex}`}>
            {text.substring(currentIndex, codeBlockStart)}
          </span>
        );
      }
      
      // 找到代码块的结束位置
      const codeBlockEnd = text.indexOf("```", codeBlockStart + 3);
      if (codeBlockEnd === -1) {
        // 如果没有找到结束标记，将剩余文本作为普通文本处理
        parts.push(
          <span key={`text-${codeBlockStart}`}>
            {text.substring(codeBlockStart)}
          </span>
        );
        break;
      }
      
      // 提取代码块内容和可能的语言标识
      const codeBlockContent = text.substring(codeBlockStart + 3, codeBlockEnd);
      const firstLineBreak = codeBlockContent.indexOf("\n");
      let code = codeBlockContent;
      let language = "";
      
      if (firstLineBreak !== -1) {
        const firstLine = codeBlockContent.substring(0, firstLineBreak).trim();
        // 如果第一行只包含字母和短横线，将其视为语言标识
        if (/^[a-zA-Z-]+$/.test(firstLine)) {
          language = firstLine;
          code = codeBlockContent.substring(firstLineBreak + 1);
        }
      }
      
      // 添加格式化的代码块
      parts.push(
        <div key={`code-${codeBlockStart}`} className="my-2">
          {language && (
            <div className="bg-gray-700 text-gray-200 text-xs px-3 py-1 rounded-t">
              {language}
            </div>
          )}
          <pre className={`bg-gray-800 text-gray-100 p-3 overflow-x-auto text-sm ${language ? 'rounded-b' : 'rounded'}`}>
            {code}
          </pre>
        </div>
      );
      
      // 更新当前索引
      currentIndex = codeBlockEnd + 3;
      codeBlockStart = text.indexOf("```", currentIndex);
    }
    
    // 添加剩余的文本
    if (currentIndex < text.length) {
      parts.push(
        <span key={`text-${currentIndex}`}>
          {text.substring(currentIndex)}
        </span>
      );
    }
    
    return <>{parts}</>;
  };

  if (isLoading && !resultData)
    return <div className="p-8 text-center">Loading...</div>;
  if (error && !resultData)
    return <div className="p-8 text-center text-red-500">{error}</div>;

  return (
    <div className="container mx-auto p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Training Data Viewer</h1>
        
        {/* 页面切换按钮 */}
        <Link 
          href="/editor" 
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
        >
          Switch to Test Data
        </Link>
      </div>

      {/* 文件选择器 */}
      {availableFiles.length > 0 && (
        <FileSelector
          files={availableFiles}
          currentFile={currentFile}
          onFileChange={handleFileChange}
        />
      )}

      <SearchBar searchTerm={searchTerm} onSearch={handleSearch} />

      {/* 在加载时显示加载消息并防止页面空白 */}
      {isLoading || isDataSlicing ? (
        <div className="p-8 text-center">
          <div className="animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mx-auto mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2 mx-auto"></div>
          </div>
          <p className="mt-4">
            {isLoading 
              ? "Loading data... This may take a moment for large datasets." 
              : "Preparing data view... Please wait."}
          </p>
        </div>
      ) : (
        <>
          {/* 显示设置引导信息 */}
          {setupMessage && (
            <div className="mb-6 p-4 bg-blue-100 text-blue-700 rounded-lg">
              <p className="font-medium">{setupMessage}</p>
              {directoryInfo && (
                <p className="mt-2 text-sm">Directory: {directoryInfo}</p>
              )}
              <p className="mt-2">
                To add training data, place JSON files in the training directory and refresh this page.
              </p>
            </div>
          )}

          {/* 添加数据集大小和性能提示 */}
          {Array.isArray(resultData) && resultData.length > 1000 && (
            <div className="mb-6 p-4 bg-blue-100 text-blue-700 rounded-lg">
              <p className="font-medium">Large Dataset Detected</p>
              <p className="mt-2 text-sm">The current dataset contains {resultData.length.toLocaleString()} records, which may affect performance.</p>
              <p className="mt-2 text-sm">Using search and pagination is recommended for better performance.</p>
            </div>
          )}

          {availableFiles.length === 0 && (
            <div className="mb-6 p-4 bg-yellow-100 text-yellow-700 rounded-lg">
              <p className="font-medium">No training data files found</p>
              <p className="mt-2">
                Please add JSON files to the training data directory and refresh this page.
              </p>
            </div>
          )}

          <div className="mt-4 mb-6">
            <PaginationControls
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={handlePageChange}
              totalItems={filteredResults?.length || 0}
            />
          </div>

          {error && (
            <div className="p-4 mb-4 bg-red-100 text-red-700 rounded-lg">
              {error}
            </div>
          )}

          {/* 添加调试信息，帮助理解数据结构 */}
          {resultData && filteredResults.length === 0 && (
            <div className="p-4 mb-4 bg-orange-100 text-orange-800 rounded-lg">
              <h4 className="font-bold">Data loaded but no results displayed</h4>
              <p className="mb-2">The data format may not be compatible with the current viewer.</p>
              <p className="text-xs">Data type: {Array.isArray(resultData) ? 'Array' : typeof resultData}</p>
              <p className="text-xs">Records: {Array.isArray(resultData) ? resultData.length : 'N/A'}</p>
            </div>
          )}

          {currentResults.length > 0 ? (
            // Display conversation items
            currentResults.map((result: ConversationItem, index: number) => (
              <div key={index} className="mb-6 bg-white shadow-md rounded-lg p-4">
                {result.system && (
                  <div className="mb-4">
                    <h3 className="text-lg font-bold mb-2">System Message</h3>
                    <p className="bg-gray-100 p-3 rounded">{result.system}</p>
                  </div>
                )}
                
                {result.cwe && result.cwe.length > 0 && (
                  <div className="mb-4">
                    <h3 className="text-lg font-bold mb-2">CWE</h3>
                    <div className="flex flex-wrap gap-2">
                      {result.cwe.map((cwe, cweIndex) => (
                        <span 
                          key={cweIndex}
                          className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-medium"
                          title={`Common Weakness Enumeration: ${cwe}`}
                        >
                          {cwe}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {result.conversations && (
                  <div className="mb-4">
                    <h3 className="text-lg font-bold mb-2">Conversations</h3>
                    {result.conversations.map((msg, msgIndex) => (
                      <div 
                        key={msgIndex} 
                        className={`mb-3 p-3 rounded ${
                          msg.from === "user" 
                            ? "bg-blue-50 border-l-4 border-blue-500" 
                            : "bg-green-50 border-l-4 border-green-500"
                        }`}
                      >
                        <div className="font-bold mb-1">
                          {msg.from === "user" ? "User" : "Assistant"}
                        </div>
                        {msg.from === "assistant" 
                          ? formatAssistantMessage(msg.value)
                          : <div className="whitespace-pre-wrap overflow-auto max-h-96">{msg.value}</div>}
                      </div>
                    ))}
                  </div>
                )}
                {result.ground_truth && (
                    <div className="mb-4">
                      <h3 className="text-lg font-bold mb-2">Ground Truth</h3>
                      <div className="bg-purple-50 border-l-4 border-purple-500 p-3 rounded">
                        <div className="whitespace-pre-wrap">{formatCodeBlocks(result.ground_truth)}</div>
                      </div>
                    </div>
                )}
                {result.idx && (
                  <div className="text-sm text-gray-500">ID: {result.idx}</div>
                )}
              </div>
            ))
          ) : (
            <div className="p-8 text-center bg-gray-100 rounded-lg">
              {resultData
                ? "No training results match your search criteria"
                : "No training data available"}
            </div>
          )}
        </>
      )}
    </div>
  );
} 