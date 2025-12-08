'use client';

import { useEffect, useState } from 'react';
import { Circle, RotateCw, CheckCircle, Clock, Radar, FileSearch, Key, Lightbulb, Wrench } from 'lucide-react';
import { AgentStage, AgentStatus, ScanProgress } from '@/types/scan';

interface ScanLoadingScreenProps {
  repositoryName: string;
  scanProgress?: ScanProgress | null;
}

export default function ScanLoadingScreen({ repositoryName, scanProgress }: ScanLoadingScreenProps) {
  const [startTime] = useState(Date.now());
  const [elapsed, setElapsed] = useState(0);

  // Timer to show elapsed time
  useEffect(() => {
    const interval = setInterval(() => {
      setElapsed(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);

    return () => clearInterval(interval);
  }, [startTime]);

  const formatElapsed = (seconds: number): string => {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const getAgentStatus = (agentKey: string): AgentStatus => {
    if (!scanProgress) return 'pending';
    return scanProgress.agents[agentKey as keyof typeof scanProgress.agents]?.status || 'pending';
  };

  const getAgentIcon = (agentKey: string) => {
    const icons: Record<string, React.ComponentType<{ className?: string }>> = {
      orchestrator: Radar,
      code_scanner: FileSearch,
      secret_detector: Key,
      context_enricher: Lightbulb,
      remediation: Wrench,
    };
    return icons[agentKey] || Circle;
  };

  const agentList = [
    { key: 'orchestrator', name: 'Orchestrator', description: 'Initializing security scan workflow' },
    { key: 'code_scanner', name: 'Code Scanner', description: 'Analyzing source code for vulnerabilities' },
    { key: 'secret_detector', name: 'Secret Detector', description: 'Scanning for hardcoded secrets and credentials' },
    { key: 'context_enricher', name: 'Context Enricher', description: 'Gathering additional security context' },
    { key: 'remediation', name: 'Remediation', description: 'Generating patches for identified issues' },
  ];

  const getStatusIcon = (status: AgentStatus) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-gray-400 flex-shrink-0" />;
      case 'in_progress':
        return <RotateCw className="w-5 h-5 text-gray-900 animate-spin flex-shrink-0" />;
      case 'error':
        return <Circle className="w-5 h-5 text-red-500 flex-shrink-0" />;
      default:
        return <Circle className="w-5 h-5 text-gray-300 flex-shrink-0" />;
    }
  };

  const getStatusBadge = (status: AgentStatus) => {
    switch (status) {
      case 'completed':
        return (
          <span className="inline-flex items-center px-2.5 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded-md">
            Done
          </span>
        );
      case 'in_progress':
        return (
          <span className="inline-flex items-center px-2.5 py-1 bg-gray-900 text-white text-xs font-medium rounded-md">
            Running
          </span>
        );
      case 'error':
        return (
          <span className="inline-flex items-center px-2.5 py-1 bg-red-100 text-red-700 text-xs font-medium rounded-md">
            Error
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2.5 py-1 bg-gray-100 text-gray-500 text-xs font-medium rounded-md">
            Pending
          </span>
        );
    }
  };

  return (
    <div className="min-h-screen bg-white py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">ShipSafe</h1>
          <p className="text-gray-600">Security Vulnerability Scanner</p>
        </div>

        {/* Repository Card with Timer */}
        <div className="bg-white border border-gray-200 rounded-xl p-6 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-medium text-gray-500 mb-1">Scanning Repository</h2>
              <p className="text-gray-900 font-mono text-base">{repositoryName}</p>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Clock className="w-4 h-4" />
              <span>{formatElapsed(elapsed)}</span>
            </div>
          </div>
        </div>

        {/* Processing Message */}
        <div className="bg-gray-50 border border-gray-200 rounded-xl p-6 mb-8">
          <div className="flex items-center gap-3">
            <RotateCw className="w-5 h-5 text-gray-900 animate-spin flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-gray-900">Analysis in Progress</p>
              <p className="text-sm text-gray-600">
                {scanProgress 
                  ? `Currently running: ${scanProgress.current_agent.replace('_', ' ')}`
                  : 'Running security agents on your repository...'}
              </p>
            </div>
          </div>
        </div>

        {/* Agent List with Real Status */}
        <div className="space-y-3">
          {agentList.map((agent) => {
            const status = getAgentStatus(agent.key);
            const IconComponent = getAgentIcon(agent.key);
            
            return (
              <div
                key={agent.key}
                className={`bg-white border rounded-xl p-5 transition-all ${
                  status === 'in_progress'
                    ? 'border-gray-900'
                    : status === 'completed'
                    ? 'border-gray-200 opacity-60'
                    : 'border-gray-200'
                }`}
              >
                <div className="flex items-start gap-4">
                  {/* Status Icon */}
                  <div className="mt-0.5">{getStatusIcon(status)}</div>

                  {/* Agent Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-1.5">
                      <IconComponent className="w-5 h-5 text-gray-700" />
                      <h3 className="text-base font-semibold text-gray-900">{agent.name}</h3>
                      {getStatusBadge(status)}
                    </div>
                    <p className="text-gray-600 text-sm">{agent.description}</p>
                    
                    {/* Show timing if available */}
                    {scanProgress && status !== 'pending' && (
                      <div className="text-xs text-gray-500 mt-2">
                        {status === 'completed' 
                          ? `Completed at ${new Date(scanProgress.agents[agent.key as keyof typeof scanProgress.agents].completed_at || '').toLocaleTimeString()}`
                          : status === 'in_progress'
                          ? `Started at ${new Date(scanProgress.agents[agent.key as keyof typeof scanProgress.agents].started_at || '').toLocaleTimeString()}`
                          : ''}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="text-center mt-8">
          <p className="text-sm text-gray-500">
            This may take a few moments depending on repository size...
          </p>
        </div>
      </div>
    </div>
  );
}
