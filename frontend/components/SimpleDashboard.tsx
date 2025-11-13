'use client';

import { useEffect, useMemo, useState } from 'react'
import { useSession } from 'next-auth/react'
import { LoginScreen } from './LoginScreen'
import { Activity, CheckCircle2, Timer, FolderGit2, Clock } from 'lucide-react'

interface GitHubRepo {
  id: number
  name: string
  full_name: string
  description: string | null
  html_url: string
  updated_at: string
  stargazers_count: number
  forks_count: number
  private: boolean
  archived: boolean
  language: string | null
}

export function SimpleDashboard() {
  const { data: session, status } = useSession()
  const [repos, setRepos] = useState<GitHubRepo[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const r = await fetch('/api/repos').then(async (res) => (res.ok ? res.json() : []))
        setRepos(r || [])
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    if (session) {
      load()
    }
  }, [session])

  const topRepos = useMemo(() => repos.slice(0, 6), [repos])

  const getTimeAgo = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`
    return `${Math.floor(diffInMinutes / 1440)}d ago`
  }

  if (status === 'loading') {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-gray-200 border-t-black rounded-full animate-spin" />
      </div>
    )
  }

  if (!session) return <LoginScreen />

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      {/* Page header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Overview</h1>
          <p className="text-gray-600 mt-1">Repositories at a glance</p>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="rounded-2xl border border-gray-200 p-5 bg-white">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Total Repos</span>
            <FolderGit2 className="w-4 h-4 text-gray-400" />
          </div>
          <div className="mt-3 text-2xl font-semibold text-gray-900">{repos.length}</div>
        </div>
        <div className="rounded-2xl border border-gray-200 p-5 bg-white">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Public Repos</span>
            <Activity className="w-4 h-4 text-gray-400" />
          </div>
          <div className="mt-3 text-2xl font-semibold text-gray-900">{repos.filter(r => !r.private).length}</div>
        </div>
        <div className="rounded-2xl border border-gray-200 p-5 bg-white">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Private Repos</span>
            <CheckCircle2 className="w-4 h-4 text-gray-400" />
          </div>
          <div className="mt-3 text-2xl font-semibold text-gray-900">{repos.filter(r => r.private).length}</div>
        </div>
        <div className="rounded-2xl border border-gray-200 p-5 bg-white">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Stars</span>
            <Timer className="w-4 h-4 text-gray-400" />
          </div>
          <div className="mt-3 text-2xl font-semibold text-gray-900">{repos.reduce((acc, r) => acc + r.stargazers_count, 0)}</div>
        </div>
      </div>

      {/* Repositories */}
      <div className="rounded-2xl border border-gray-200 bg-white">
        <div className="p-5 border-b border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900">Recent Repositories</h2>
        </div>
        <div className="p-5">
          {loading ? (
            <div className="h-32 flex items-center justify-center">
              <div className="w-6 h-6 border-4 border-gray-200 border-t-black rounded-full animate-spin" />
            </div>
          ) : topRepos.length ? (
            <ul className="divide-y divide-gray-100">
              {topRepos.map((r) => (
                <li key={r.id} className="py-3 flex items-center justify-between">
                  <div>
                    <div className="text-sm font-medium text-gray-900">{r.name}</div>
                    <div className="text-xs text-gray-500 flex items-center gap-2">
                      <Clock className="w-3 h-3" />
                      <span>Updated {getTimeAgo(r.updated_at)}</span>
                      {r.language && <span>• {r.language}</span>}
                    </div>
                  </div>
                  <a href={r.html_url} target="_blank" rel="noopener noreferrer" className="text-xs text-gray-600 hover:text-gray-900">
                    View
                  </a>
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-sm text-gray-600 text-center py-8">
              No repositories yet. Click the Sync button in the header to fetch your GitHub repositories.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
