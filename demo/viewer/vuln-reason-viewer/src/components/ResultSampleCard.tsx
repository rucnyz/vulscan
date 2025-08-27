// components/ResultSampleCard.tsx
import React, { Suspense } from "react";
import { ResultSample } from "@/lib/types";
import { CopyButton } from "./CopyButton";
const CodeDiff = React.lazy(() => import("./CodeDiff"));
const MarkdownRenderer = React.lazy(() => import("./MarkdownRenderer"));

interface ResultSampleCardProps {
  result: ResultSample;
}

const ResultSampleCard: React.FC<ResultSampleCardProps> = ({ result }) => {
  // change the first code block in input to "..."
  const input = result.input.replace(
    /```\n([\s\S]*?)\n```/,
    "```\n...code above...\n```"
  );
  return (
      <div className="bg-white shadow-md rounded-lg p-4 mb-6">
        {/* Vulnerability status section */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <DataIdStatus dataId={result.idx}/>
          <VulnerabilityStatus
              label="Actual Status"
              isVuln={result.is_vuln}
              vulnType={result.vuln_type}
          />
          <VulnerabilityStatus
              label="Predicted Status"
              isVuln={result.pred_is_vuln}
              vulnType={result.pred_vuln_type}
          />
          <JudgeStatus judge={result.judge}/>
        </div>

        {/* Code and Input/Output sections */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Code section - Left column */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <h3 className="text-lg font-semibold">Code</h3>
              {result.pair_code && (
                  <CopyButton text={result.pair_code} label="Copy Paired Code"/>
              )}
              <CopyButton text={result.code} label="Copy Code"/>
            </div>
            <Suspense fallback={<div>Loading code diff...</div>}>
              <CodeDiff
                  originalCode={result.code}
                  newCode={result.pair_code}
                  language="python"
                  maxHeight="80vh"
              />
            </Suspense>
          </div>

          {/* Right column with all outputs stacked */}
          <div className="flex flex-col">
            {/* Unparsed Output section */}
            <div className="mb-6">
              <div className="flex justify-between items-center mb-2">
                <h3 className="text-lg font-semibold">Unparsed Output</h3>
                <CopyButton
                    text={result.unparsed_pred_vuln_type} label="Copy Unparsed"
                />
              </div>
              <div className="border rounded-md p-4 max-h-[10vh] overflow-auto">
                <div className="font-mono text-sm">
                  <div><span className="text-gray-600">Vulnerability Type:</span> {result.unparsed_pred_vuln_type}</div>
                </div>
              </div>
            </div>

            {/* Input section */}
            <div className="mb-6">
              <div className="flex justify-between items-center mb-2">
                <h3 className="text-lg font-semibold">Input</h3>
                <CopyButton text={result.input} label="Copy Input"/>
              </div>
              <div className="border rounded-md p-4 max-h-[20vh] overflow-auto">
                <Suspense fallback={<div>Loading input...</div>}>
                  <MarkdownRenderer content={input}/>
                </Suspense>
              </div>
            </div>

            {/* Output section */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <h3 className="text-lg font-semibold">Output</h3>
                <CopyButton text={result.output} label="Copy Output"/>
              </div>
              <div className="border rounded-md p-4 max-h-[40vh] overflow-auto">
                <Suspense fallback={<div>Loading output...</div>}>
                  <MarkdownRenderer content={result.output}/>
                </Suspense>
              </div>
            </div>
          </div>
        </div>
      </div>
  );
};

// Helper component for vulnerability status display
const VulnerabilityStatus: React.FC<{
  label: string;
  isVuln: boolean | null;
  vulnType: string | null;
}> = ({label, isVuln, vulnType}) => {
  const statusColor =
      isVuln === null ? "bg-gray-300" : isVuln ? "bg-red-500" : "bg-green-500";
  const statusText =
      isVuln === null ? "Invalid" : isVuln ? "Vulnerable" : "Safe";
  return (
      <div>
        <p className="text-sm font-medium text-gray-500">{label}</p>
        <div className="flex items-center mt-1">
        <span
            className={`inline-block w-3 h-3 rounded-full mr-2 ${statusColor}`}
        ></span>
          <span className="font-medium">
          {statusText}
            {isVuln && vulnType && ` (${vulnType})`}
        </span>
        </div>
      </div>
  );
};

// Check TP, TN, FP, FN, similar style as above
const JudgeStatus: React.FC<{
  judge: string;
}> = ({judge}) => {
  const status = judge.toUpperCase();
  const statusColor = ["TP", "TN"].includes(status)
      ? "bg-green-500"
      : "bg-red-500";
  const statusText = `${status}`;
  return (
      <div>
        <p className="text-sm font-medium text-gray-500">Judge</p>
        <div className="flex items-center mt-1">
        <span
            className={`inline-block w-3 h-3 rounded-full mr-2 ${statusColor}`}
        ></span>
          <span className="font-medium">{statusText}</span>
        </div>
      </div>
  );
};

// Helper component for displaying the data ID
const DataIdStatus: React.FC<{
  dataId: number | string;
}> = ({dataId}) => {
  return (
      <div>
        <p className="text-sm font-medium text-gray-500">Data ID</p>
        <div className="flex items-center mt-1">
          <span className="font-medium">{dataId}</span>
        </div>
      </div>
  );
};

export default ResultSampleCard;
