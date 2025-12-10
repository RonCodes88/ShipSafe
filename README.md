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

### Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- Python 3.9+
- GitHub account
- OpenAI API key (for secret classification)

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/ShipSafe.git
cd ShipSafe
```

### 2. Backend Setup

Install Python dependencies:

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory:

```bash
OPENAI_API_KEY=your_openai_api_key
GITHUB_TOKEN=your_github_personal_access_token
```

Start the backend server:

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### 3. Frontend Setup

Install Node dependencies:

```bash
cd frontend
npm install
```

Create a GitHub OAuth App:
1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click "New OAuth App"
3. Set **Homepage URL** to `http://localhost:3000`
4. Set **Callback URL** to `http://localhost:3000/api/auth/callback/github`
5. Copy your Client ID and Client Secret

Create a `.env.local` file in the `frontend/` directory:

```bash
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
NEXTAUTH_SECRET=your_nextauth_secret  # Generate with: openssl rand -base64 32
NEXTAUTH_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 4. Start Scanning

1. Sign in with your GitHub account
2. Select a repository to scan
3. View vulnerability reports and automated fixes

---

For detailed setup instructions, see [`frontend/README.md`](frontend/README.md).

