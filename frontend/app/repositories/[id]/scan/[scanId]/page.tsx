'use client';

import { useState, useEffect } from 'react';
import { useParams, useSearchParams, useRouter } from 'next/navigation';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { ScanData } from '@/types/scan';
import { startScan } from '@/lib/scan-client';
import ScanLoadingScreen from '@/components/scan/ScanLoadingScreen';
import ImprovedScanResultsLayout from '@/components/scan/ImprovedScanResultsLayout';

export default function ScanResultsPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();

  const repoUrl = searchParams.get('repo_url');
  const repoId = params.id as string;

  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<ScanData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const triggerScan = async () => {
    if (!repoUrl) {
      setError('Repository URL is missing');
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await startScan(repoUrl);

      if (response.success && response.data) {
        setData(response.data);
      } else {
        setError(response.error || 'Scan failed');
      }
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    triggerScan();
  }, [repoUrl]);

  const handleRescan = () => {
    triggerScan();
  };

  // Loading state
  if (loading) {
    return (
      <ScanLoadingScreen
        repositoryName={
          repoUrl ? repoUrl.replace('https://github.com/', '').replace('.git', '') : 'Repository'
        }
      />
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-8">
        <div className="max-w-md w-full">
          <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
            <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Scan Failed</h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <div className="flex flex-col gap-3">
              <button
                onClick={handleRescan}
                className="flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                <RefreshCw className="w-4 h-4" />
                Retry Scan
              </button>
              <button
                onClick={() => router.push('/repositories')}
                className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
              >
                Back to Repositories
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Results state
  if (data) {
    return <ImprovedScanResultsLayout scanData={data} onRescan={handleRescan} />;
  }

  // Fallback
  return null;
}
