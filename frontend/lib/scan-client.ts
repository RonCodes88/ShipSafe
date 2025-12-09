// Client-side wrapper for scan API

import { ScanResponse } from '@/types/scan';

export interface ScanStartResponse {
  success: boolean;
  scan_id?: string;
  error?: string;
}

/**
 * Trigger a security scan for a repository
 * @param repoUrl - GitHub repository URL
 * @returns ScanStartResponse with scan_id for tracking
 */
export async function startScan(repoUrl: string): Promise<ScanStartResponse> {
  try {
    const response = await fetch('/api/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ repo_url: repoUrl }),
    });

    const data = await response.json();

    if (!response.ok) {
      return {
        success: false,
        error: data.error || `HTTP ${response.status}: ${response.statusText}`,
      };
    }

    return data as ScanStartResponse;
  } catch (error: any) {
    console.error('Scan client error:', error);

    return {
      success: false,
      error: error.message || 'Network error. Please check your connection.',
    };
  }
}

/**
 * Get scan results
 * @param scanId - Scan ID
 * @returns Scan results
 */
export async function getScanResults(scanId: string): Promise<ScanResponse> {
  try {
    const response = await fetch(`/api/scan/results/${scanId}`);
    const data = await response.json();

    if (!response.ok) {
      return {
        success: false,
        data: null,
        error: data.error || `HTTP ${response.status}: ${response.statusText}`,
      };
    }

    if (data.status === 'completed') {
      return {
        success: true,
        data: data.data,
        error: null,
      };
    } else if (data.status === 'error') {
      return {
        success: false,
        data: null,
        error: data.error || 'Scan failed',
      };
    }

    // Still running
    return {
      success: false,
      data: null,
      error: 'Scan is still in progress',
    };
  } catch (error: any) {
    console.error('Get results error:', error);

    return {
      success: false,
      data: null,
      error: error.message || 'Network error. Please check your connection.',
    };
  }
}
