'use client';

import { AlertTriangle, Shield, Key, FileCode, Clock } from 'lucide-react';
import { ScanData } from '@/types/scan';

interface ScanSummaryCardProps {
  scanData: ScanData;
}

export default function ScanSummaryCard({ scanData }: ScanSummaryCardProps) {
  const { scan_summary, metadata, repository } = scanData;
  const hasIssues = scan_summary.total_issues > 0;

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
      {/* Repository Header */}
      <div className="flex items-start justify-between mb-6">
        <div className="flex-1">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            {repository.full_name || repository.name || 'Security Scan Results'}
          </h2>
          {repository.description && (
            <p className="text-gray-600 text-sm">{repository.description}</p>
          )}
        </div>
        {hasIssues ? (
          <div className="flex items-center gap-2 px-4 py-2 bg-red-50 border border-red-200 rounded-lg">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <span className="font-semibold text-red-900">Issues Found</span>
          </div>
        ) : (
          <div className="flex items-center gap-2 px-4 py-2 bg-green-50 border border-green-200 rounded-lg">
            <Shield className="w-5 h-5 text-green-600" />
            <span className="font-semibold text-green-900">All Clear</span>
          </div>
        )}
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Total Issues */}
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">Total Issues</span>
            <FileCode className="w-4 h-4 text-gray-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-gray-900">
              {scan_summary.total_issues}
            </span>
            <span className="text-sm text-gray-500">
              {scan_summary.total_issues === 1 ? 'issue' : 'issues'}
            </span>
          </div>
        </div>

        {/* Vulnerabilities */}
        <div className="bg-orange-50 rounded-lg p-4 border border-orange-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-orange-700">Vulnerabilities</span>
            <AlertTriangle className="w-4 h-4 text-orange-500" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-orange-900">
              {scan_summary.vulnerabilities_count}
            </span>
            <span className="text-sm text-orange-600">
              {scan_summary.vulnerabilities_count === 1 ? 'vuln' : 'vulns'}
            </span>
          </div>
        </div>

        {/* Secrets */}
        <div className="bg-red-50 rounded-lg p-4 border border-red-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-red-700">Secrets</span>
            <Key className="w-4 h-4 text-red-500" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-red-900">
              {scan_summary.secrets_count}
            </span>
            <span className="text-sm text-red-600">
              {scan_summary.secrets_count === 1 ? 'secret' : 'secrets'}
            </span>
          </div>
        </div>

        {/* Scan Time */}
        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-blue-700">Scan Time</span>
            <Clock className="w-4 h-4 text-blue-500" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-blue-900">
              {metadata.execution_time.toFixed(1)}
            </span>
            <span className="text-sm text-blue-600">seconds</span>
          </div>
        </div>
      </div>

      {/* Agents Invoked */}
      {metadata.agents_invoked.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <span className="font-medium">Agents:</span>
            <div className="flex items-center gap-1">
              {metadata.agents_invoked.map((agent, idx) => (
                <span key={idx} className="flex items-center">
                  <span className="px-2 py-1 bg-gray-100 rounded text-xs font-mono">
                    {agent}
                  </span>
                  {idx < metadata.agents_invoked.length - 1 && (
                    <span className="mx-1 text-gray-400">→</span>
                  )}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Errors */}
      {metadata.errors.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 text-orange-500 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <span className="text-sm font-medium text-orange-700">
                {metadata.errors.length} warning{metadata.errors.length !== 1 ? 's' : ''} during scan:
              </span>
              <ul className="mt-2 space-y-1">
                {metadata.errors.map((error, idx) => (
                  <li key={idx} className="text-sm text-orange-600 font-mono">
                    {error}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

