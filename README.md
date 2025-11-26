# ShipSafe

ShipSafe is an AI-powered security vulnerability scanner for GitHub repositories. It automatically analyzes your code for security vulnerabilities, detects hardcoded secrets and credentials, and generates code patches to fix identified issues.

## What It Does

- Scans GitHub repositories for security vulnerabilities using AI-powered code analysis
- Detects hardcoded secrets, API keys, tokens, and credentials
- Generates automated code patches and remediation suggestions
- Provides detailed vulnerability reports with severity levels and fix recommendations

## How It Works

Connect your GitHub account to scan your repositories. ShipSafe uses AI agents to analyze your code, identify security issues, and suggest fixes. The system scans for common vulnerabilities like SQL injection, XSS, CSRF, and other security risks, while also detecting exposed secrets and credentials.

## Tech Stack

- Frontend: Next.js, TypeScript, Tailwind CSS
- Backend: Python, LangChain, LangGraph
- AI Models: CodeBERT (vulnerability detection), PatchLM (patch generation)
- Authentication: GitHub OAuth

## Getting Started

See the `frontend/README.md` for setup instructions.

