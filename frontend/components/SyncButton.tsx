import React, { useState } from 'react';

interface SyncButtonProps {
  onSyncComplete?: () => void;
}

export default function SyncButton({ onSyncComplete }: SyncButtonProps) {
  const [isLoading, setIsLoading] = useState(false);

  const handleSync = async () => {
    setIsLoading(true);
    

    try {
      const response = await fetch('/api/sync-repos', {
        method: 'POST',
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to sync repositories');
      }

      if (onSyncComplete) {
        onSyncComplete();
      }

      console.log('Sync successful:', data);
      // Reload the page to refresh the repository list
      window.location.reload();
    } catch (error) {
      console.error('Sync failed:', error);
      alert('Failed to sync repositories. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button
      onClick={handleSync}
      disabled={isLoading}
      title={isLoading ? 'Syncing…' : 'Sync repositories'}
      aria-label={isLoading ? 'Syncing…' : 'Sync repositories'}
      className={`
        inline-flex items-center gap-2 px-3 py-1.5 rounded-md text-sm border transition-colors
        ${isLoading
          ? 'bg-gray-50 text-gray-400 border-gray-200 cursor-not-allowed'
          : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-50'}
      `}
    >
      <svg
        className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`}
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
        />
      </svg>
      <span>{isLoading ? 'Syncing' : 'Sync'}</span>
    </button>
  );
}

