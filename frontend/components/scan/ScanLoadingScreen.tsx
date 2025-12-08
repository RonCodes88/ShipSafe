'use client';

import { useEffect, useState } from 'react';
import { Circle, RotateCw, CheckCircle } from 'lucide-react';
import { AgentStage, AgentStatus } from '@/types/scan';

interface ScanLoadingScreenProps {
  repositoryName: string;
}

const AGENT_STAGES: AgentStage[] = [
  { name: 'Orchestrator', status: 'pending', duration: 2000 },
  { name: 'Code Scanner', status: 'pending', duration: 5000 },
  { name: 'Secret Detector', status: 'pending', duration: 3000 },
  { name: 'Context Enricher', status: 'pending', duration: 4000 },
  { name: 'Remediation', status: 'pending', duration: 3000 },
];

export default function ScanLoadingScreen({ repositoryName }: ScanLoadingScreenProps) {
  const [stages, setStages] = useState<AgentStage[]>(AGENT_STAGES);
  const [progress, setProgress] = useState(0);
  const [currentStageIndex, setCurrentStageIndex] = useState(0);

  useEffect(() => {
    // Simulate stage progression
    const totalDuration = AGENT_STAGES.reduce((acc, stage) => acc + (stage.duration || 0), 0);
    let elapsed = 0;

    const interval = setInterval(() => {
      elapsed += 200;
      const newProgress = Math.min((elapsed / totalDuration) * 100, 95); // Stop at 95%
      setProgress(newProgress);

      // Update current stage based on elapsed time
      let accumulatedTime = 0;
      for (let i = 0; i < AGENT_STAGES.length; i++) {
        accumulatedTime += AGENT_STAGES[i].duration || 0;
        if (elapsed < accumulatedTime) {
          setCurrentStageIndex(i);
          break;
        }
      }

      // Update stage statuses
      setStages((prev) =>
        prev.map((stage, index) => {
          let accumulatedTime = 0;
          for (let i = 0; i <= index; i++) {
            accumulatedTime += AGENT_STAGES[i].duration || 0;
          }

          if (elapsed >= accumulatedTime) {
            return { ...stage, status: 'completed' as AgentStatus };
          } else if (index === currentStageIndex) {
            return { ...stage, status: 'in_progress' as AgentStatus };
          }
          return { ...stage, status: 'pending' as AgentStatus };
        })
      );
    }, 200);

    return () => clearInterval(interval);
  }, [currentStageIndex]);

  const getStageIcon = (status: AgentStatus) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'in_progress':
        return <RotateCw className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'error':
        return <Circle className="w-5 h-5 text-red-500" />;
      default:
        return <Circle className="w-5 h-5 text-gray-300" />;
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="w-full max-w-2xl px-8">
        {/* Logo/Branding */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">ShipSafe</h1>
          <p className="text-gray-600">Security Vulnerability Scanner</p>
        </div>

        {/* Repository Info */}
        <div className="text-center mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-2">Scanning Repository</h2>
          <p className="text-lg text-gray-600 font-mono">{repositoryName}</p>
        </div>

        {/* Agent Stages */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <div className="space-y-4">
            {stages.map((stage, index) => (
              <div
                key={stage.name}
                className={`flex items-center gap-4 p-4 rounded-xl transition-all duration-300 ${
                  stage.status === 'in_progress'
                    ? 'bg-blue-50 border border-blue-200 scale-105'
                    : stage.status === 'completed'
                    ? 'bg-green-50 border border-green-100'
                    : 'bg-gray-50 border border-gray-100'
                }`}
              >
                {/* Icon */}
                <div className="flex-shrink-0">{getStageIcon(stage.status)}</div>

                {/* Stage Name */}
                <div className="flex-1">
                  <p
                    className={`font-medium ${
                      stage.status === 'in_progress'
                        ? 'text-blue-700'
                        : stage.status === 'completed'
                        ? 'text-green-700'
                        : 'text-gray-500'
                    }`}
                  >
                    {stage.name}
                  </p>
                </div>

                {/* Status Label */}
                <div className="flex-shrink-0">
                  {stage.status === 'completed' && (
                    <span className="text-sm text-green-600 font-medium">Completed</span>
                  )}
                  {stage.status === 'in_progress' && (
                    <span className="text-sm text-blue-600 font-medium animate-pulse">
                      In Progress
                    </span>
                  )}
                  {stage.status === 'pending' && (
                    <span className="text-sm text-gray-400">Pending</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Overall Progress</span>
            <span className="text-sm font-medium text-gray-700">{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-purple-600 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Info Text */}
        <p className="text-center text-sm text-gray-500">
          Analyzing your repository for security vulnerabilities and secrets...
        </p>
      </div>
    </div>
  );
}
