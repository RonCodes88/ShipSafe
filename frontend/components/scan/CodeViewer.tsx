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
    <div className="h-full flex flex-col bg-gray-900">
      {/* Simple File Header */}
      <div className="px-4 py-2 bg-gray-800 text-gray-300 text-sm font-mono">
        {file.path}
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
                className={`flex items-start group hover:bg-gray-800 transition-colors ${
                  isHighlighted ? 'bg-gray-800' : ''
                }`}
              >
                {/* Line Number */}
                <div className="flex-shrink-0 w-16 text-right pr-4 py-1 text-gray-500 select-none bg-gray-900 border-r border-gray-700">
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
                  <code className="text-gray-200">{line || ' '}</code>
                </pre>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
