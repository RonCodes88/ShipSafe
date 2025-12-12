# ShipSafe
ShipSafe is an multi-agent system that scans your code, detect vulnerabilities, and generate automated fixes for you.

<img width="1431" height="890" alt="image" src="https://github.com/user-attachments/assets/c0026a95-85ec-4596-9ee7-032b7ebc8ca0" />

## Demo
[https://www.youtube.com/watch?v=BzTmxkDC3cU&feature=youtu.be](https://www.youtube.com/watch?v=BzTmxkDC3cU&feature=youtu.be)

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

