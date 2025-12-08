// Type definitions for security scan data structures

export interface ScanResponse {
  success: boolean;
  data: ScanData | null;
  error: string | null;
}

export interface ScanData {
  scan_summary: ScanSummary;
  repository: RepositoryMetadata;
  vulnerabilities: string[];  // TOON format strings
  secrets: string[];          // TOON format strings
  files?: Record<string, string>;  // { file_path: content } - optional
  metadata: ScanMetadata;
}

export interface ScanSummary {
  total_issues: number;
  vulnerabilities_count: number;
  secrets_count: number;
}

export interface RepositoryMetadata {
  name?: string;
  full_name?: string;
  description?: string;
  html_url?: string;
  default_branch?: string;
  language?: string;
  stargazers_count?: number;
  forks_count?: number;
  [key: string]: any;  // Allow additional GitHub metadata fields
}

export interface ScanMetadata {
  agents_invoked: string[];
  errors: string[];
  status: string;
  execution_time: number;
}

// Parsed vulnerability/secret types
export interface ParsedVulnerability {
  id: string;
  type: 'vulnerability' | 'secret';

  // Common fields
  explanation: string;
  formattedCode: string;

  // Vulnerability-specific fields (from enriched data)
  category?: string;
  severity?: string;
  file?: string;
  lineStart?: number;
  lineEnd?: number;

  // CVSS-like metrics
  attackVector?: string;
  attackComplexity?: string;
  privilegesRequired?: string;
  userInteraction?: string;
  impactConfidentiality?: string;
  impactIntegrity?: string;
  impactAvailability?: string;

  // Secret-specific fields
  fixType?: string;
  recommendation?: string;
  secretType?: string;

  // Raw TOON data for debugging
  raw?: Record<string, string>;
}

export interface FileWithVulnerabilities {
  path: string;
  content: string;
  vulnerabilities: ParsedVulnerability[];
  language?: string;
}

// Agent stage status for loading screen
export type AgentStatus = 'pending' | 'in_progress' | 'completed' | 'error';

export interface AgentStage {
  name: string;
  status: AgentStatus;
  duration?: number;  // Estimated duration in ms
}

// Real-time scan progress types
export interface AgentProgress {
  status: AgentStatus;
  started_at: string | null;
  completed_at: string | null;
  error?: string;
}

export interface ScanProgress {
  scan_id: string;
  repo_url: string;
  status: 'running' | 'completed' | 'error';
  current_agent: string;
  agents: {
    orchestrator: AgentProgress;
    code_scanner: AgentProgress;
    secret_detector: AgentProgress;
    context_enricher: AgentProgress;
    remediation: AgentProgress;
  };
  started_at: string;
  completed_at: string | null;
  error?: string;
}

// Severity levels
export type SeverityLevel = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';

// Severity color mapping
export const SEVERITY_COLORS: Record<SeverityLevel, string> = {
  CRITICAL: 'text-red-600 bg-red-50 border-red-200',
  HIGH: 'text-orange-600 bg-orange-50 border-orange-200',
  MEDIUM: 'text-amber-600 bg-amber-50 border-amber-200',
  LOW: 'text-blue-600 bg-blue-50 border-blue-200',
  INFO: 'text-gray-600 bg-gray-50 border-gray-200',
};

// Severity icon colors for markers
export const SEVERITY_ICON_COLORS: Record<SeverityLevel, string> = {
  CRITICAL: 'text-red-600',
  HIGH: 'text-orange-600',
  MEDIUM: 'text-amber-500',
  LOW: 'text-blue-500',
  INFO: 'text-gray-500',
};
