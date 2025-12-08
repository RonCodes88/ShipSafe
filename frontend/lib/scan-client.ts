// Client-side wrapper for scan API

import { ScanResponse } from '@/types/scan';

/**
 * Trigger a security scan for a repository
 * @param repoUrl - GitHub repository URL
 * @returns ScanResponse with results or error
 */
export async function startScan(repoUrl: string): Promise<ScanResponse> {
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
        data: null,
        error: data.error || `HTTP ${response.status}: ${response.statusText}`,
      };
    }

    return data as ScanResponse;
  } catch (error: any) {
    console.error('Scan client error:', error);

    return {
      success: false,
      data: null,
      error: error.message || 'Network error. Please check your connection.',
    };
  }
}
