'use client';

import { Github, ExternalLink, Clock } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';

// Interface for GitHub repositories
interface GitHubRepo {
  id: number
  name: string
  full_name: string
  description: string | null
  html_url: string
  default_branch: string
  private: boolean
  language: string | null
  updated_at: string
  clone_url: string
  created_at: string
  pushed_at: string
  size: number
  stargazers_count: number
  watchers_count: number
  forks_count: number
  open_issues_count: number
  topics: string[]
  archived: boolean
  disabled: boolean
  visibility: string
}

export function ProjectGrid() {
  const [repos, setRepos] = useState<GitHubRepo[]>([]);
  const [loading, setLoading] = useState(true);
  const [needsSync, setNeedsSync] = useState(false);
  const searchParams = useSearchParams();
  const query = (searchParams.get('search') || '').trim().toLowerCase();
  const router = useRouter();

  useEffect(() => {
    const fetchRepos = async () => {
      try {
        const response = await fetch('/api/repos');
        if (response.ok) {
          const data = await response.json();
          setRepos(data);
        } else if (response.status === 404) {
          const errorData = await response.json();
          if (errorData.shouldSync) {
            setNeedsSync(true);
          }
        }
      } catch (error) {
        console.error('Error fetching repositories:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchRepos();
  }, []);

  const getTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 60) {
      return `${diffInMinutes} minutes ago`;
    } else if (diffInMinutes < 1440) {
      return `${Math.floor(diffInMinutes / 60)} hours ago`;
    } else {
      return `${Math.floor(diffInMinutes / 1440)} days ago`;
    }
  };

  const filtered = query
    ? repos.filter((r) => {
        const hay = [
          r.name,
          r.full_name,
          r.description || '',
          r.language || '',
          ...(r.topics || []),
        ]
          .join(' ')
          .toLowerCase();
        return hay.includes(query);
      })
    : repos;

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-4 border-gray-200 border-t-black rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  if (needsSync) {
    return (
      <div className="max-w-7xl mx-auto">
        <div className="text-center py-12">
          <div className="mb-4">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 1.79 4 4 4h8c2.21 0 4-1.79 4-4V7c0-2.21-1.79-4-4-4H8c-2.21 0-4 1.79-4 4z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 9h6v6H9z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No repositories found</h3>
          <p className="text-gray-600 mb-4">
            Click the "Sync" button in the header to fetch your GitHub repositories.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header with unique styling */}
      <div className="mb-8">
        <div className="bg-white border border-gray-200 rounded-2xl p-8 text-gray-900">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">Repository Hub</h1>
              <p className="text-gray-600 text-lg">Discover and manage your GitHub projects</p>
              <div className="flex items-center gap-6 mt-4 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>{filtered.filter(r => !r.private).length} Public</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                  <span>{filtered.filter(r => r.private).length} Private</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                  <span>{filtered.filter(r => r.archived).length} Archived</span>
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-4xl font-bold">{filtered.length}</div>
              <div className="text-gray-600">{query ? 'Matching Repositories' : 'Total Repositories'}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Project Grid - Unique Card Design */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
        {filtered.map((repo) => (
          <div
            key={repo.id}
            className="group relative bg-white rounded-3xl border-2 border-gray-100 hover:border-gray-300 hover:shadow-2xl transition-all duration-300 overflow-hidden"
          >
            {/* Card Header with Gradient */}
            <div className="relative p-6 pb-4">
              {/* Status Indicator */}
              <div className="absolute top-4 right-4">
                <div className={`w-3 h-3 rounded-full ${
                  (Date.now() - new Date(repo.updated_at).getTime()) / (1000 * 60 * 60) < 24 
                    ? 'bg-green-400 shadow-green-400/50 shadow-lg' 
                    : 'bg-gray-400'
                }`}></div>
              </div>

              {/* Repository Name and Privacy */}
              <div className="flex items-start gap-3 mb-3">
                <div className="flex-shrink-0 w-12 h-12 bg-black rounded-2xl flex items-center justify-center text-white font-bold text-lg">
                  {repo.name.charAt(0).toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-bold text-lg text-gray-900 truncate group-hover:text-black transition-colors">
                    {repo.name}
                  </h3>
                  <div className="flex items-center gap-2 mt-1">
                    {repo.private ? (
                      <span className="inline-flex items-center gap-1 text-xs bg-orange-100 text-orange-700 px-2 py-1 rounded-full">
                        🔒 Private
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
                        🌍 Public
                      </span>
                    )}
                    {repo.archived && (
                      <span className="inline-flex items-center gap-1 text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                        📦 Archived
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Description */}
              <p className="text-sm text-gray-600 line-clamp-2 mb-4 leading-relaxed">
                {repo.description || 'No description available for this repository.'}
              </p>

              {/* Language and Stats */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${
                    repo.language === 'TypeScript' ? 'bg-gray-600' :
                    repo.language === 'JavaScript' ? 'bg-yellow-500' :
                    repo.language === 'Python' ? 'bg-green-600' :
                    repo.language === 'Vue' ? 'bg-green-500' :
                    repo.language === 'Java' ? 'bg-orange-600' :
                    repo.language === 'Go' ? 'bg-cyan-500' :
                    repo.language === 'Rust' ? 'bg-orange-800' :
                    'bg-gray-400'
                  }`}></div>
                  <span className="text-sm font-medium text-gray-700">
                    {repo.language || 'Unknown'}
                  </span>
                </div>
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <div className="flex items-center gap-1">
                    <span>⭐</span>
                    <span>{repo.stargazers_count}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <span>🍴</span>
                    <span>{repo.forks_count}</span>
                  </div>
                </div>
              </div>

              {/* Updated Time */}
              <div className="flex items-center gap-2 text-xs text-gray-500 mb-4">
                <Clock className="w-4 h-4" />
                <span>Updated {getTimeAgo(repo.updated_at)}</span>
              </div>
            </div>

            {/* Card Footer with Actions */}
            <div className="px-6 pb-6">
              <div className="flex">
                <a 
                  href={repo.html_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="flex-1 flex items-center justify-center gap-2 py-3 px-4 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl font-medium transition-colors text-sm"
                >
                  <Github className="w-4 h-4" />
                  View Code
                </a>
              </div>
            </div>

            {/* Hover Effect Overlay */}
            <div className="absolute inset-0 bg-black/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none rounded-3xl"></div>
          </div>
        ))}
      </div>
    </div>
  );
}
