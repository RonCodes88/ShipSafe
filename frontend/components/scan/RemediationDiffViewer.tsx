'use client';

import { useState } from 'react';
import { Copy, Check, ChevronDown, ChevronUp } from 'lucide-react';

interface RemediationDiffViewerProps {
  diff: string;
  explanation: string;
}

export default function RemediationDiffViewer({ diff, explanation }: RemediationDiffViewerProps) {
  const [copied, setCopied] = useState(false);
  const [isExpanded, setIsExpanded] = useState(true);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(diff);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  // Parse diff to extract meaningful lines
  const diffLines = diff.split('\n').filter((line) => line.trim());
  const isTooLong = diffLines.length > 20;

  return (
    <div className="space-y-3">
      {/* Explanation */}
      {explanation && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-900">{explanation}</p>
        </div>
      )}

      {/* Diff Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h4 className="text-sm font-semibold text-gray-700">Suggested Fix</h4>
          {isTooLong && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1"
            >
              {isExpanded ? (
                <>
                  <ChevronUp className="w-3 h-3" /> Collapse
                </>
              ) : (
                <>
                  <ChevronDown className="w-3 h-3" /> Expand
                </>
              )}
            </button>
          )}
        </div>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
        >
          {copied ? (
            <>
              <Check className="w-3 h-3 text-green-600" />
              <span className="text-green-600">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-3 h-3" />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>

      {/* Diff Content */}
      <div
        className={`bg-gray-900 rounded-lg overflow-hidden ${
          !isExpanded && isTooLong ? 'max-h-48' : ''
        }`}
      >
        <div className="p-4 overflow-x-auto">
          <pre className="text-sm font-mono">
            {diffLines.map((line, index) => {
              let lineClass = 'text-gray-300';
              let bgClass = '';

              if (line.startsWith('-')) {
                lineClass = 'text-red-400';
                bgClass = 'bg-red-900/20';
              } else if (line.startsWith('+')) {
                lineClass = 'text-green-400';
                bgClass = 'bg-green-900/20';
              } else if (line.startsWith('@@')) {
                lineClass = 'text-blue-400';
              } else if (line.startsWith('diff') || line.startsWith('---') || line.startsWith('+++')) {
                lineClass = 'text-gray-500';
              }

              return (
                <div key={index} className={`${bgClass} ${lineClass} px-2 -mx-2`}>
                  <code>{line}</code>
                </div>
              );
            })}
          </pre>
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 text-xs text-gray-500">
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-red-900/20 border border-red-400/30 rounded" />
          <span>Removed</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-green-900/20 border border-green-400/30 rounded" />
          <span>Added</span>
        </div>
      </div>
    </div>
  );
}
