'use client';

import { useState, useMemo } from 'react';
import { ArrowLeft, FileCode } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { ScanData, ParsedVulnerability } from '@/types/scan';
import { parseAllFindings } from '@/lib/toon-parser';
import ScanSummaryCard from './ScanSummaryCard';
import IssueListView from './IssueListView';
import CodeViewer from './CodeViewer';
import VulnerabilitySidePanel from './VulnerabilitySidePanel';

interface ScanResultsLayoutProps {
  scanData: ScanData;
  onRescan?: () => void;
}

export default function ScanResultsLayout({
  scanData,
  onRescan,
}: ScanResultsLayoutProps) {
  const router = useRouter();
  const [selectedIssue, setSelectedIssue] = useState<ParsedVulnerability | null>(null);
  const [isPanelOpen, setIsPanelOpen] = useState(false);

  // Parse all findings
  const allIssues = useMemo(() => {
    return parseAllFindings(scanData.vulnerabilities || [], scanData.secrets || []);
  }, [scanData.vulnerabilities, scanData.secrets]);

  const hasIssues = allIssues.length > 0;

  // Get file content for selected issue
  const getFileContent = (filePath: string): string => {
    return scanData.files?.[filePath] || '';
  };

  const handleIssueClick = (issue: ParsedVulnerability) => {
    setSelectedIssue(issue);
    setIsPanelOpen(true);
  };

  const handleNavigate = (direction: 'prev' | 'next') => {
    if (!selectedIssue) return;

    const currentIndex = allIssues.findIndex((i) => i.id === selectedIssue.id);
    if (currentIndex === -1) return;

    let newIndex = currentIndex;
    if (direction === 'prev' && currentIndex > 0) {
      newIndex = currentIndex - 1;
    } else if (direction === 'next' && currentIndex < allIssues.length - 1) {
      newIndex = currentIndex + 1;
    }

    setSelectedIssue(allIssues[newIndex]);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-5">
        <div className="max-w-[2000px] mx-auto">
          <button
            onClick={() => router.push('/repositories')}
            className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 transition-colors mb-5"
          >
            <ArrowLeft className="w-4 h-4" />
            <span className="font-medium">Back to Repositories</span>
          </button>

          {/* Summary */}
          <ScanSummaryCard scanData={scanData} />
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 overflow-hidden">
        {hasIssues ? (
            <div className="h-full flex max-w-[2000px] mx-auto">
            {/* Left Sidebar - Issue List */}
              <div className="w-96 bg-white border-r border-gray-200 flex flex-col">
              <div className="p-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">
                  Security Issues ({allIssues.length})
                </h2>
                <p className="text-sm text-gray-600 mt-1">
                  Click on an issue to view details and remediation
                </p>
              </div>
                <div className="flex-1 overflow-y-auto p-4">
                <IssueListView
                  issues={allIssues}
                  onIssueClick={handleIssueClick}
                  selectedIssueId={selectedIssue?.id}
                />
              </div>
            </div>

            {/* Right Side - Code Viewer */}
            <div className="flex-1 bg-gray-50 overflow-hidden flex items-center justify-center">
              {selectedIssue && selectedIssue.file ? (
                <CodeViewer
                  file={{
                    path: selectedIssue.file,
                    content: getFileContent(selectedIssue.file),
                    vulnerabilities: allIssues.filter((i) => i.file === selectedIssue.file),
                  }}
                  onMarkerClick={handleIssueClick}
                  highlightedLine={selectedIssue.lineStart}
                />
              ) : (
                <div className="text-center p-12">
                  <FileCode className="w-20 h-20 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500 text-lg font-medium">
                    Select an issue to view the code
                  </p>
                  <p className="text-gray-400 text-sm mt-2">
                    Choose from the list on the left to see the vulnerable code and suggested fixes
                  </p>
                </div>
              )}
            </div>
          </div>
        ) : (
          // No issues found
          <div className="h-full flex items-center justify-center">
            <div className="text-center max-w-md">
              <div className="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg
                  className="w-12 h-12 text-green-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <h2 className="text-3xl font-bold text-gray-900 mb-3">All Clear!</h2>
              <p className="text-gray-600 mb-8">
                No security vulnerabilities or hardcoded secrets were detected in this repository.
              </p>
              <div className="bg-green-50 border border-green-200 rounded-lg px-6 py-4">
                <p className="text-sm text-green-800">
                  <span className="font-semibold">Scan completed in</span>{' '}
                  {scanData.metadata.execution_time.toFixed(2)}s
                </p>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Vulnerability Detail Side Panel */}
      {selectedIssue && (
        <VulnerabilitySidePanel
          isOpen={isPanelOpen}
          vulnerability={selectedIssue}
          currentIndex={allIssues.findIndex((i) => i.id === selectedIssue.id)}
          totalCount={allIssues.length}
          onClose={() => setIsPanelOpen(false)}
          onNavigate={handleNavigate}
        />
      )}
    </div>
  );
}

