# ShipSafe Frontend

This is the Next.js frontend for ShipSafe, an AI-powered security vulnerability scanner for GitHub repositories.

## Getting Started

### 1. Install Dependencies

```bash
npm install
# or
yarn install
# or
pnpm install
```

### 2. Set Up Environment Variables

#### Create a GitHub OAuth App

Each developer needs to create their own GitHub OAuth App:

1. Go to https://github.com/settings/developers
2. Click "New OAuth App"
3. Fill in the form:
   - **Application name**: `ShipSafe` (or your choice)
   - **Homepage URL**: `http://localhost:3000`
   - **Authorization callback URL**: `http://localhost:3000/api/auth/callback/github`
4. Click "Register application"
5. Copy the **Client ID** and generate a new **Client Secret**

#### Create `.env.local` File

Create a `.env.local` file in the `frontend/` directory with the following variables:

```bash
# GitHub OAuth Configuration
# Get these from your GitHub OAuth App: https://github.com/settings/developers
GITHUB_CLIENT_ID=your_github_client_id_here
GITHUB_CLIENT_SECRET=your_github_client_secret_here

# NextAuth Configuration
# Generate a random secret: openssl rand -base64 32
NEXTAUTH_SECRET=your_nextauth_secret_here
NEXTAUTH_URL=http://localhost:3000

# Backend API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Note**: Each developer should generate their own `NEXTAUTH_SECRET` using `openssl rand -base64 32`

### 3. Run the Development Server

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the application.

**Note**: Make sure the backend server is running at `http://localhost:8000` before using the application.

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── api/               # API routes (NextAuth, scan endpoints)
│   ├── repositories/      # Repository listing and scanning pages
│   └── page.tsx           # Home page
├── components/            # React components
│   ├── scan/             # Scan-related components (results, viewers, etc.)
│   └── ...               # Other UI components
├── lib/                   # Utility functions and API clients
└── types/                # TypeScript type definitions
```

## Features

- **GitHub OAuth Authentication**: Secure login with GitHub
- **Repository Management**: View and select repositories to scan
- **Real-time Scanning**: Live progress updates during security scans
- **Vulnerability Viewer**: Interactive code viewer with highlighted issues
- **Remediation Suggestions**: AI-generated patches and fix explanations

## Learn More

- [Main README](../README.md) - Full project documentation
- [Next.js Documentation](https://nextjs.org/docs) - Next.js features and API
