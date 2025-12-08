'use client';

import { useState, useEffect, useMemo } from 'react';
import { ArrowLeft, RefreshCw, CheckCircle, AlertTriangle } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { ScanData, ParsedVulnerability, FileWithVulnerabilities } from '@/types/scan';
import { parseAllFindings, groupVulnerabilitiesByFile } from '@/lib/toon-parser';
import CodeViewer from './CodeViewer';
import VulnerabilitySidePanel from './VulnerabilitySidePanel';

interface ScanResultsLayoutProps {
  scanData: ScanData;
  onRescan?: () => void;
}

export default function ScanResultsLayout({ scanData, onRescan }: ScanResultsLayoutProps) {
  const router = useRouter();
  const [selectedVulnerabilityIndex, setSelectedVulnerabilityIndex] = useState<number | null>(null);
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  const [currentFileIndex, setCurrentFileIndex] = useState(0);

  // Parse all vulnerabilities and secrets
  const allVulnerabilities = useMemo(() => {
    return parseAllFindings(scanData.vulnerabilities || [], scanData.secrets || []);
  }, [scanData.vulnerabilities, scanData.secrets]);

  // Group by file
  const fileMap = useMemo(() => {
    return groupVulnerabilitiesByFile(allVulnerabilities);
  }, [allVulnerabilities]);

  // Convert to array for easier navigation
  const filesWithVulnerabilities = useMemo(() => {
    const files: FileWithVulnerabilities[] = [];
    fileMap.forEach((vulnerabilities, path) => {
      files.push({
        path,
        content: scanData.files?.[path] || '', // Use actual file content from scan data
        vulnerabilities,
      });
    });
    return files.sort((a, b) => a.path.localeCompare(b.path));
  }, [fileMap, scanData.files]);

  const currentFile = filesWithVulnerabilities[currentFileIndex];
  const hasVulnerabilities = allVulnerabilities.length > 0;

  // Handle marker click
  const handleMarkerClick = (vulnerability: ParsedVulnerability) => {
    const index = allVulnerabilities.findIndex((v) => v.id === vulnerability.id);
    if (index !== -1) {
      setSelectedVulnerabilityIndex(index);
      setIsPanelOpen(true);
    }
  };

  // Handle panel navigation
  const handleNavigate = (direction: 'prev' | 'next') => {
    if (selectedVulnerabilityIndex === null) return;

    let newIndex = selectedVulnerabilityIndex;
    if (direction === 'prev' && selectedVulnerabilityIndex > 0) {
      newIndex = selectedVulnerabilityIndex - 1;
    } else if (direction === 'next' && selectedVulnerabilityIndex < allVulnerabilities.length - 1) {
      newIndex = selectedVulnerabilityIndex + 1;
    }

    setSelectedVulnerabilityIndex(newIndex);

    // Switch file if necessary
    const newVuln = allVulnerabilities[newIndex];
    const newFileIndex = filesWithVulnerabilities.findIndex((f) => f.path === newVuln.file);
    if (newFileIndex !== -1 && newFileIndex !== currentFileIndex) {
      setCurrentFileIndex(newFileIndex);
    }
  };

  // Keyboard shortcuts for global navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (isPanelOpen) return; // Panel handles its own keyboard shortcuts

      if (e.key === 'ArrowLeft' && selectedVulnerabilityIndex !== null && selectedVulnerabilityIndex > 0) {
        e.preventDefault();
        handleNavigate('prev');
      } else if (
        e.key === 'ArrowRight' &&
        selectedVulnerabilityIndex !== null &&
        selectedVulnerabilityIndex < allVulnerabilities.length - 1
      ) {
        e.preventDefault();
        handleNavigate('next');
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedVulnerabilityIndex, allVulnerabilities.length, isPanelOpen]);

  const selectedVulnerability =
    selectedVulnerabilityIndex !== null ? allVulnerabilities[selectedVulnerabilityIndex] : null;

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-[1800px] mx-auto flex items-center justify-between">
          {/* Left: Back button */}
          <button
            onClick={() => router.push('/repositories')}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span className="font-medium">Back to Repositories</span>
          </button>

          {/* Center: Repository info */}
          <div className="flex-1 text-center">
            <h1 className="text-xl font-bold text-gray-900">
              {scanData.repository.full_name || scanData.repository.name || 'Repository Scan'}
            </h1>
            <div className="flex items-center justify-center gap-4 mt-1">
              <div className="flex items-center gap-2">
                {hasVulnerabilities ? (
                  <AlertTriangle className="w-4 h-4 text-orange-500" />
                ) : (
                  <CheckCircle className="w-4 h-4 text-green-500" />
                )}
                <span className="text-sm text-gray-600">
                  {hasVulnerabilities
                    ? `${scanData.scan_summary.total_issues} issue${scanData.scan_summary.total_issues !== 1 ? 's' : ''} found`
                    : 'No issues found'}
                </span>
              </div>
              {scanData.scan_summary.vulnerabilities_count > 0 && (
                <span className="text-sm text-gray-600">
                  {scanData.scan_summary.vulnerabilities_count} vulnerability{scanData.scan_summary.vulnerabilities_count !== 1 ? 'ies' : ''}
                </span>
              )}
              {scanData.scan_summary.secrets_count > 0 && (
                <span className="text-sm text-gray-600">
                  {scanData.scan_summary.secrets_count} secret{scanData.scan_summary.secrets_count !== 1 ? 's' : ''}
                </span>
              )}
            </div>
          </div>

          {/* Right: Actions */}
          <div className="flex items-center gap-3">
            {onRescan && (
              <button
                onClick={onRescan}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium text-sm"
              >
                <RefreshCw className="w-4 h-4" />
                Rescan
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex overflow-hidden">
        {hasVulnerabilities ? (
          <>
            {/* File Tabs (if multiple files) */}
            {filesWithVulnerabilities.length > 1 && (
              <div className="w-64 bg-white border-r border-gray-200 overflow-y-auto">
                <div className="p-4">
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">Files with Issues</h3>
                  <div className="space-y-1">
                    {filesWithVulnerabilities.map((file, index) => (
                      <button
                        key={file.path}
                        onClick={() => setCurrentFileIndex(index)}
                        className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                          currentFileIndex === index
                            ? 'bg-blue-50 text-blue-700 font-medium'
                            : 'text-gray-600 hover:bg-gray-50'
                        }`}
                      >
                        <div className="font-mono truncate">{file.path.split('/').pop()}</div>
                        <div className="text-xs text-gray-500 mt-1">
                          {file.vulnerabilities.length} issue{file.vulnerabilities.length !== 1 ? 's' : ''}
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Code Viewer */}
            <div className="flex-1 overflow-hidden">
              {currentFile ? (
                <CodeViewer
                  file={currentFile}
                  onMarkerClick={handleMarkerClick}
                  highlightedLine={selectedVulnerability?.lineStart}
                />
              ) : (
                <div className="h-full flex items-center justify-center text-gray-500">
                  Select a file to view
                </div>
              )}
            </div>

            {/* Side Panel */}
            <VulnerabilitySidePanel
              isOpen={isPanelOpen}
              vulnerability={selectedVulnerability}
              currentIndex={selectedVulnerabilityIndex || 0}
              totalCount={allVulnerabilities.length}
              onClose={() => setIsPanelOpen(false)}
              onNavigate={handleNavigate}
            />
          </>
        ) : (
          // No vulnerabilities found
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">All Clear!</h2>
              <p className="text-gray-600 mb-6">No security issues or secrets detected in this repository.</p>
              <div className="bg-green-50 border border-green-200 rounded-lg px-6 py-4 inline-block">
                <p className="text-sm text-green-800">
                  Scan completed in {scanData.metadata.execution_time.toFixed(2)}s
                </p>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer with Metadata */}
      <footer className="bg-white border-t border-gray-200 px-6 py-3">
        <div className="max-w-[1800px] mx-auto flex items-center justify-between text-xs text-gray-500">
          <div>
            Scan completed in {scanData.metadata.execution_time.toFixed(2)}s
            {scanData.metadata.agents_invoked.length > 0 && (
              <span className="ml-4">
                Agents: {scanData.metadata.agents_invoked.join(' → ')}
              </span>
            )}
          </div>
          {scanData.metadata.errors.length > 0 && (
            <div className="text-orange-600">
              {scanData.metadata.errors.length} warning{scanData.metadata.errors.length !== 1 ? 's' : ''}
            </div>
          )}
        </div>
      </footer>
    </div>
  );
}
