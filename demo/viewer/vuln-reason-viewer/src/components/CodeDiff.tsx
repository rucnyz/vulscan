// components/CodeDiff.tsx
import React, { useMemo } from 'react';
import { diffLines, diffWordsWithSpace } from 'diff';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneLight } from 'react-syntax-highlighter/dist/cjs/styles/prism';

interface CodeDiffProps {
  originalCode: string;
  newCode: string | null | undefined;
  language?: string;
  showLineNumbers?: boolean;
  maxHeight?: string;
}

const CodeDiff: React.FC<CodeDiffProps> = ({
  originalCode,
  newCode,
  language = 'cpp',
  showLineNumbers = true,
  maxHeight = '80vh'
}) => {
  // If there's no new code, just show the original
  if (!newCode) {
    return (
      <div className="rounded-md overflow-auto" style={{ maxHeight }}>
        <SyntaxHighlighter
          language={language}
          style={oneLight}
          wrapLines={true}
          showLineNumbers={showLineNumbers}
          customStyle={{ margin: 0, fontSize: '0.8rem' }}
          lineProps={{ style: { whiteSpace: 'pre-wrap' } }}
        >
          {originalCode}
        </SyntaxHighlighter>
      </div>
    );
  }

  // Calculate the diff
  const differences = useMemo(() => {
    return diffLines(originalCode, newCode);
  }, [originalCode, newCode]);

  // Process the diff to create line-by-line tracking 
  const processedCode = useMemo(() => {
    let lines: { text: string; status: 'added' | 'removed' | 'unchanged' }[] = [];

    differences.forEach(part => {
      const partLines = part.value.split('\n');
      // If this is the last empty line after a split, skip it
      const linesCount = part.value.endsWith('\n') ? partLines.length - 1 : partLines.length;
      
      for (let i = 0; i < linesCount; i++) {
        const status = part.added ? 'added' : part.removed ? 'removed' : 'unchanged';
        lines.push({ text: partLines[i], status });
      }
    });

    return lines;
  }, [differences]);

  // Combine the code into a single string for the highlighter
  const combinedCode = processedCode.map(line => line.text).join('\n');

  return (
    <div className="rounded-md overflow-hidden">
      <div className="bg-gray-200 text-black px-4 py-2 text-sm font-medium">
        Code Differences
      </div>
      <div className="overflow-auto" style={{ maxHeight }}>
        <SyntaxHighlighter
          language={language}
          style={oneLight}
          showLineNumbers={showLineNumbers}
          wrapLines={true}
          lineProps={(lineNumber) => {
            const status = processedCode[lineNumber - 1]?.status;
            let style = { display: 'block', backgroundColor: 'transparent', whiteSpace: 'pre-wrap'};
            
            if (status === 'added') {
              style = { ...style, backgroundColor: '#dbffdb' }; // Light green for additions
            } else if (status === 'removed') {
              style = { ...style, backgroundColor: '#ffecec' }; // Light red for removals
            }
            
            return { style };
          }}
          customStyle={{ margin: 0, fontSize: '0.8rem' }}
        >
          {combinedCode}
        </SyntaxHighlighter>
      </div>
    </div>
  );
};

export default CodeDiff;