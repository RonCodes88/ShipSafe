import { NextResponse } from 'next/server'
import { getServerSession } from 'next-auth/next'
import { RepoDatabase } from '@/lib/database'
import { authOptions } from '../auth/[...nextauth]/route'

export async function GET() {
  try {
    const session = await getServerSession(authOptions)
    
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Get repositories from local JSON database
    const repos = RepoDatabase.getAllRepos()
    
    if (repos.length === 0) {
      return NextResponse.json({ 
        error: 'No repositories found. Please sync your repositories first.',
        shouldSync: true 
      }, { status: 404 })
    }

    // Sort by most recently updated
    const sortedRepos = repos.sort((a, b) => 
      new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    )

    return NextResponse.json(sortedRepos)
  } catch (error) {
    console.error('Error fetching repositories:', error)
    return NextResponse.json({ error: 'Failed to fetch repositories' }, { status: 500 })
  }
}

