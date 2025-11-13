import fs from 'fs';
import path from 'path';

const DB_PATH = path.join(process.cwd(), 'data', 'repos.json');

export interface Repository {
  id: number;
  name: string;
  full_name: string;
  description: string | null;
  html_url: string;
  default_branch: string;
  private: boolean;
  language: string | null;
  updated_at: string;
  clone_url: string;
  created_at: string;
  pushed_at: string;
  size: number;
  stargazers_count: number;
  watchers_count: number;
  forks_count: number;
  open_issues_count: number;
  topics: string[];
  archived: boolean;
  disabled: boolean;
  visibility: string;
}

export class RepoDatabase {
  private static ensureDbExists() {
    const dir = path.dirname(DB_PATH);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    if (!fs.existsSync(DB_PATH)) {
      fs.writeFileSync(DB_PATH, JSON.stringify([], null, 2));
    }
  }

  static getAllRepos(): Repository[] {
    this.ensureDbExists();
    try {
      const data = fs.readFileSync(DB_PATH, 'utf-8');
      return JSON.parse(data);
    } catch (error) {
      console.error('Error reading repos database:', error);
      return [];
    }
  }

  static saveRepos(repos: Repository[]): void {
    this.ensureDbExists();
    try {
      fs.writeFileSync(DB_PATH, JSON.stringify(repos, null, 2));
      console.log(`Saved ${repos.length} repositories to database`);
    } catch (error) {
      console.error('Error saving repos to database:', error);
      throw error;
    }
  }

  static addRepo(repo: Repository): void {
    const repos = this.getAllRepos();
    const existingIndex = repos.findIndex(r => r.id === repo.id);
    
    if (existingIndex >= 0) {
      repos[existingIndex] = repo; // Update existing
    } else {
      repos.push(repo); // Add new
    }
    
    this.saveRepos(repos);
  }

  static deleteRepo(repoId: number): void {
    const repos = this.getAllRepos();
    const filteredRepos = repos.filter(r => r.id !== repoId);
    this.saveRepos(filteredRepos);
  }

  static getRepoCount(): number {
    return this.getAllRepos().length;
  }

  static getLastSyncTime(): string | null {
    const repos = this.getAllRepos();
    if (repos.length === 0) return null;
    
    // Return the most recent update time
    const lastUpdate = repos.reduce((latest, repo) => {
      const repoTime = new Date(repo.updated_at).getTime();
      return repoTime > latest ? repoTime : latest;
    }, 0);
    
    return new Date(lastUpdate).toISOString();
  }
}

