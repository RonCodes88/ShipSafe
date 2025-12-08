'use client';

import { FileWithVulnerabilities, ParsedVulnerability } from '@/types/scan';
import { getVulnerabilityAtLine } from '@/lib/toon-parser';
import VulnerabilityMarker from './VulnerabilityMarker';

interface CodeViewerProps {
  file: FileWithVulnerabilities;
  onMarkerClick: (vulnerability: ParsedVulnerability) => void;
  highlightedLine?: number;
}

export default function CodeViewer({ file, onMarkerClick, highlightedLine }: CodeViewerProps) {
  const lines = file.content.split('\n');

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* File Header */}
      <div className="bg-gray-800 text-white px-6 py-3 flex items-center justify-between border-b border-gray-700">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 rounded-full bg-red-500" />
          <div className="w-3 h-3 rounded-full bg-yellow-500" />
          <div className="w-3 h-3 rounded-full bg-green-500" />
        </div>
        <span className="text-sm font-mono font-medium">{file.path}</span>
        <div className="flex items-center gap-2">
          {file.language && (
            <span className="text-xs bg-gray-700 px-2 py-1 rounded">{file.language}</span>
          )}
          <span className="text-xs text-gray-400">
            {file.vulnerabilities.length} issue{file.vulnerabilities.length !== 1 ? 's' : ''}
          </span>
        </div>
      </div>

      {/* Code Content */}
      <div className="flex-1 overflow-auto">
        <div className="font-mono text-sm">
          {lines.map((line, index) => {
            const lineNumber = index + 1;
            const vulnerability = getVulnerabilityAtLine(file.vulnerabilities, lineNumber);
            const isHighlighted = highlightedLine === lineNumber;

            return (
              <div
                key={lineNumber}
                className={`flex items-start group hover:bg-gray-100 transition-colors ${
                  isHighlighted ? 'bg-yellow-50' : ''
                }`}
              >
                {/* Line Number */}
                <div className="flex-shrink-0 w-16 text-right pr-4 py-1 text-gray-500 select-none bg-gray-50 border-r border-gray-200">
                  {lineNumber}
                </div>

                {/* Vulnerability Marker */}
                <div className="flex-shrink-0 w-8 flex items-center justify-center">
                  {vulnerability && (
                    <VulnerabilityMarker
                      vulnerability={vulnerability}
                      onClick={() => onMarkerClick(vulnerability)}
                    />
                  )}
                </div>

                {/* Code Line */}
                <pre className="flex-1 px-4 py-1 overflow-x-auto">
                  <code className="text-gray-800">{line || ' '}</code>
                </pre>
              </div>
            );
          })}
        </div>
      </div>

      {/* Footer with stats */}
      <div className="bg-gray-800 text-gray-400 px-6 py-2 text-xs flex items-center justify-between border-t border-gray-700">
        <span>
          {lines.length} line{lines.length !== 1 ? 's' : ''}
        </span>
        <span className="font-mono">{file.path.split('.').pop()?.toUpperCase()}</span>
      </div>
    </div>
  );
}
