# ShipSafe
ShipSafe uses AI agents to scan your code, detect vulnerabilities, and generate automated fixes for you.

## What It Does

- Scans GitHub repositories for security vulnerabilities using AI-powered code analysis
- Detects hardcoded secrets, API keys, tokens, and credentials
- Generates automated code patches and remediation suggestions
- Provides detailed vulnerability reports with severity levels and fix recommendations

## How It Works

Connect your GitHub account to start scanning. ShipSafe uses a multi-agent system built on LangGraph and LangChain to analyze your code in multiple stages:

**1. Repository Analysis:**
The system fetches your repository and breaks down each source file using AST (Abstract Syntax Tree) parsing, which identifies individual functions and their exact locations.

**2. Vulnerability Detection:**
Each function is analyzed by CodeBERT, a specialized AI model trained to detect security vulnerabilities. The model assigns a confidence score to flag potential issues like SQL injection, XSS, CSRF, and other common attack vectors.

**3. Secret Detection:**
A parallel agent scans for exposed credentials and API keys using pattern matching and entropy analysis to catch hardcoded secrets that shouldn't be in your code.

**4. Context & Remediation:**
AI agents enrich each finding with severity ratings, root-cause explanations, and automatically generate code patches to fix the issues. You get both the vulnerable code and the suggested fix, side-by-side.

The entire pipeline runs automatically, giving you actionable security insights in minutes.
## Tech Stack

- Frontend: Next.js, TypeScript, Tailwind CSS
- Backend: Python, LangChain, LangGraph
- AI Models: CodeBERT (vulnerability detection), OpenAI
- Authentication: GitHub OAuth

## Getting Started

See the `frontend/README.md` for setup instructions.

