'use client';

import { AlertTriangle, Key } from 'lucide-react';
import { ScanData } from '@/types/scan';

interface ScanSummaryCardProps {
  scanData: ScanData;
}

export default function ScanSummaryCard({ scanData }: ScanSummaryCardProps) {
  const { scan_summary, repository } = scanData;

  return (
    <div>
      {/* Repository Title */}
      <h1 className="text-2xl font-bold text-gray-900 mb-4">
        {repository.full_name || repository.name || 'Security Scan Results'}
      </h1>

      {/* Simple Stats Bar */}
      <div className="flex items-center gap-6 text-sm text-gray-700">
        <span className="font-medium">
          {scan_summary.total_issues} security {scan_summary.total_issues === 1 ? 'issue' : 'issues'}
        </span>
        
        <span className="text-gray-300">|</span>
        
        <span className="flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-red-500" />
          <span>{scan_summary.vulnerabilities_count} {scan_summary.vulnerabilities_count === 1 ? 'vulnerability' : 'vulnerabilities'}</span>
        </span>
        
        <span className="text-gray-300">|</span>
        
        <span className="flex items-center gap-2">
          <Key className="w-4 h-4 text-purple-500" />
          <span>{scan_summary.secrets_count} {scan_summary.secrets_count === 1 ? 'secret' : 'secrets'}</span>
        </span>
      </div>
    </div>
  );
}

