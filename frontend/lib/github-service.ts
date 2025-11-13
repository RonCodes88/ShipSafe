import { Octokit } from '@octokit/rest';
import { Repository } from './database';

export class GitHubService {
  private octokit: Octokit;

  constructor(accessToken: string) {
    this.octokit = new Octokit({
      auth: accessToken,
    });
  }

  async fetchAllRepositories(): Promise<Repository[]> {
    try {
      console.log('Fetching all repositories from GitHub...');
      
      // Fetch all repositories (public and private)
      const repositories: Repository[] = [];
      let page = 1;
      let hasMore = true;

      while (hasMore) {
        console.log(`Fetching page ${page}...`);
        
        const { data } = await this.octokit.rest.repos.listForAuthenticatedUser({
          sort: 'updated',
          per_page: 100, // Maximum per page
          page,
          type: 'all', // Include public, private, and forks
        });

        if (data.length === 0) {
          hasMore = false;
        } else {
          repositories.push(...data.map(repo => ({
            id: repo.id,
            name: repo.name,
            full_name: repo.full_name,
            description: repo.description,
            html_url: repo.html_url,
            default_branch: repo.default_branch || 'main',
            private: repo.private,
            language: repo.language,
            updated_at: repo.updated_at || new Date().toISOString(),
            clone_url: repo.clone_url || '',
            created_at: repo.created_at || new Date().toISOString(),
            pushed_at: repo.pushed_at || repo.updated_at || new Date().toISOString(),
            size: repo.size,
            stargazers_count: repo.stargazers_count,
            watchers_count: repo.watchers_count,
            forks_count: repo.forks_count,
            open_issues_count: repo.open_issues_count,
            topics: repo.topics || [],
            archived: repo.archived,
            disabled: repo.disabled,
            visibility: repo.visibility || (repo.private ? 'private' : 'public'),
          })));
          
          page++;
        }
      }

      console.log(`Successfully fetched ${repositories.length} repositories`);
      return repositories;
    } catch (error) {
      console.error('Error fetching repositories from GitHub:', error);
      throw error;
    }
  }

  async getUserInfo() {
    try {
      const { data } = await this.octokit.rest.users.getAuthenticated();
      return {
        login: data.login,
        name: data.name,
        avatar_url: data.avatar_url,
        public_repos: data.public_repos,
        total_private_repos: data.total_private_repos,
        owned_private_repos: data.owned_private_repos,
      };
    } catch (error) {
      console.error('Error fetching user info:', error);
      throw error;
    }
  }
}

