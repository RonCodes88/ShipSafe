import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { GitHubService } from '@/lib/github-service';
import { authOptions } from '../auth/[...nextauth]/route';

export async function POST() {
  try {
    const session: any = await getServerSession(authOptions);
    
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized - No session' }, { status: 401 });
    }
    
    if (!session.accessToken) {
      return NextResponse.json({ error: 'Unauthorized - No access token' }, { status: 401 });
    }

    console.log('Starting repository sync...');
    
    const githubService = new GitHubService(session.accessToken);
    
    // Fetch all repositories from GitHub (no persistence)
    const repositories = await githubService.fetchAllRepositories();
    
    // Also fetch user info for additional stats
    const userInfo = await githubService.getUserInfo();
    
    console.log(`Sync completed: ${repositories.length} repositories fetched`);
    
    return NextResponse.json({
      success: true,
      message: `Fetched ${repositories.length} repositories`,
      stats: {
        total_repos: repositories.length,
        public_repos: repositories.filter(r => !r.private).length,
        private_repos: repositories.filter(r => r.private).length,
        archived_repos: repositories.filter(r => r.archived).length,
        user_info: userInfo,
        last_sync: new Date().toISOString(),
      }
    });
    
  } catch (error) {
    console.error('Error syncing repositories:', error);
    return NextResponse.json({ 
      error: 'Failed to sync repositories',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}

export async function GET() {
  try {
    const session: any = await getServerSession(authOptions);
    if (!session?.accessToken) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }
    const githubService = new GitHubService(session.accessToken);
    const repos = await githubService.fetchAllRepositories();
    const userInfo = await githubService.getUserInfo();

    return NextResponse.json({
      repos,
      stats: {
        total_repos: repos.length,
        public_repos: repos.filter(r => !r.private).length,
        private_repos: repos.filter(r => r.private).length,
        archived_repos: repos.filter(r => r.archived).length,
        user_info: userInfo,
        last_sync: new Date().toISOString(),
      }
    });
  } catch (error) {
    console.error('Error fetching repositories from database:', error);
    return NextResponse.json({ error: 'Failed to fetch repositories' }, { status: 500 });
  }
}

