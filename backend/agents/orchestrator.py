"""Orchestrator Agent - Entry point and coordinator for vulnerability scans."""

from typing import Dict, Any, Optional
import httpx
from .base_agent import BaseAgent, AgentConfig
from graph.state import ScanState




class OrchestratorAgent(BaseAgent):
    """
    Orchestrator fetches GitHub repo info using a token passed in ScanState.
    Prepares the environment for downstream agents.
    """

    def __init__(self, http_client: httpx.AsyncClient, config: AgentConfig = None, ):
        self.client = http_client
        super().__init__(config)

    async def _fetch_repo_metadata(
        self, repo_url: str, token: str
    ) -> Dict[str, Any]:
        """Fetch repo metadata (size, language, etc.) using GitHub REST API."""
        owner, repo = repo_url.replace("https://github.com/", "").split("/")
        api_url = f"https://api.github.com/repos/{owner}/{repo}"

        headers = {"Authorization": f"Bearer {token}"}

       
        res = await self.client.get(api_url, headers=headers)

        if res.status_code != 200:
            raise RuntimeError(
                f"GitHub repo metadata fetch failed: {res.text}"
            )

        return res.json()

    async def _fetch_repo_tree(
        self, repo_url: str, token: str
    ) -> Dict[str, Any]:
        """Fetch the repo file tree (list of files)."""
        owner, repo = repo_url.replace("https://github.com/", "").split("/")
        api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD?recursive=1"

        headers = {"Authorization": f"Bearer {token}"}

        res = await self.client.get(api_url, headers=headers)

        if res.status_code != 200:
            raise RuntimeError(
                f"GitHub repo tree fetch failed: {res.text}"
            )

        return res.json().get("tree", [])

    async def _fetch_file_content(
        self, repo_url: str, file_path: str, token: str
    ) -> Optional[str]:
        """Fetch raw file content from GitHub."""
        owner, repo = repo_url.replace("https://github.com/", "").split("/")
        api_url = f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/{file_path}"

        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient() as client:
            res = await client.get(api_url, headers=headers)

        return res.text if res.status_code == 200 else None

    async def _execute(self, state: ScanState) -> Dict[str, Any]:
        """
        Orchestrate by loading GitHub repository metadata & file tree.
        Prepares the context for downstream agents.
        """
        repo_url = state.get("repo_url")
        token = state.get("github_token") 

        if not repo_url:
            raise ValueError("Missing repo_url in ScanState")
        if not token:
            raise ValueError("Missing github_token in ScanState")

        self.logger.info(f"Fetching GitHub metadata for {repo_url}")

        metadata = await self._fetch_repo_metadata(repo_url, token)

        tree = await self._fetch_repo_tree(repo_url, token)

        files = {}
        for item in tree:
            if item["type"] == "blob":   
                path = item["path"]
                content = await self._fetch_file_content(repo_url, path, token)
                if content is not None:
                    files[path] = content

        self.logger.info(
            f"Loaded {len(files)} source files for vulnerability scanning"
        )


        return {
            "repo_metadata": metadata,
            "files": files,
        }
