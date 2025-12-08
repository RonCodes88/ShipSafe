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
          className={`w-full text-left p-4 rounded-lg border transition-all ${
            selectedIssueId === issue.id
              ? 'bg-blue-50 border-blue-300 shadow-sm'
              : 'bg-white border-gray-200 hover:border-gray-300 hover:shadow-sm'
          }`}
        >
          <div className="flex items-start gap-3">
            {/* Icon */}
            <div className="mt-1">{getTypeIcon(issue.type)}</div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              {/* Header */}
              <div className="flex items-center gap-2 mb-2">
                {getSeverityBadge(issue.severity || 'MEDIUM')}
                <span className="text-xs font-medium text-gray-500 uppercase">
                  {issue.type === 'secret' ? issue.secretType || 'Secret' : issue.category}
                </span>
              </div>

              {/* Description */}
              <div className="text-sm text-gray-900 font-medium mb-2 line-clamp-2">
                {issue.explanation || issue.raw?.summary || 'Security issue detected'}
              </div>

              {/* Location */}
              <div className="flex items-center gap-4 text-xs text-gray-600">
                {issue.file && (
                  <div className="flex items-center gap-1">
                    <FileCode className="w-3 h-3" />
                    <span className="font-mono truncate max-w-[200px]" title={issue.file}>
                      {issue.file}
                    </span>
                  </div>
                )}
                {issue.lineStart && (
                  <div className="flex items-center gap-1">
                    <MapPin className="w-3 h-3" />
                    <span className="font-mono">
                      {issue.lineEnd && issue.lineEnd !== issue.lineStart
                        ? `Lines ${issue.lineStart}-${issue.lineEnd}`
                        : `Line ${issue.lineStart}`}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Arrow */}
            <ChevronRight className={`w-5 h-5 flex-shrink-0 transition-colors ${
              selectedIssueId === issue.id ? 'text-blue-600' : 'text-gray-400'
            }`} />
          </div>
        </button>
      ))}
    </div>
  );
}

