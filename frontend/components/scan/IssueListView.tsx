'use client';

import { AlertTriangle, Key, FileCode, MapPin, ChevronRight } from 'lucide-react';
import { ParsedVulnerability } from '@/types/scan';
import { SEVERITY_COLORS, SEVERITY_ICON_COLORS, SeverityLevel } from '@/types/scan';

interface IssueListViewProps {
  issues: ParsedVulnerability[];
  onIssueClick: (issue: ParsedVulnerability) => void;
  selectedIssueId?: string | null;
}

export default function IssueListView({ issues, onIssueClick, selectedIssueId }: IssueListViewProps) {
  const getSeverityBadge = (severity: string) => {
    const sev = (severity?.toUpperCase() || 'MEDIUM') as SeverityLevel;
    const colorClass = SEVERITY_COLORS[sev] || SEVERITY_COLORS.MEDIUM;
    
    return (
      <span className={`px-2 py-1 text-xs font-semibold rounded border ${colorClass}`}>
        {sev}
      </span>
    );
  };

  const getTypeIcon = (type: string) => {
    if (type === 'secret') {
      return <Key className="w-4 h-4 text-red-500" />;
    }
    return <AlertTriangle className="w-4 h-4 text-orange-500" />;
  };

  if (issues.length === 0) {
    return (
      <div className="text-center py-12">
        <FileCode className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <p className="text-gray-500">No issues found</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {issues.map((issue) => (
        <button
          key={issue.id}
          onClick={() => onIssueClick(issue)}
          className={`w-full text-left p-3 rounded-lg border transition-all ${
            selectedIssueId === issue.id
              ? 'bg-blue-50 border-blue-300'
              : 'bg-white border-gray-200 hover:bg-gray-50'
          }`}
        >
          {/* Severity Badge */}
          <div className="mb-2">
            {getSeverityBadge(issue.severity || 'MEDIUM')}
          </div>

          {/* Title */}
          <h3 className="font-semibold text-gray-900 mb-1">
            {issue.type === 'secret' 
              ? (issue.secretType || 'HARDCODED SECRET').toUpperCase()
              : (issue.category || 'VULNERABILITY').toUpperCase()}
          </h3>

          {/* Description */}
          <p className="text-sm text-gray-600 mb-2 line-clamp-2">
            {issue.explanation || issue.raw?.summary || 'Security issue detected'}
          </p>

          {/* File Location */}
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <FileCode className="w-3 h-3" />
            <span className="font-mono truncate" title={issue.file}>
              {issue.file || 'unknown'}
            </span>
            {issue.lineStart && (
              <span className="font-mono">
                • L{issue.lineStart}{issue.lineEnd && issue.lineEnd !== issue.lineStart ? `-${issue.lineEnd}` : ''}
              </span>
            )}
          </div>
        </button>
      ))}
    </div>
  );
}

