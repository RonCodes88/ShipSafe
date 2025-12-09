'use client';

import { Github } from 'lucide-react';
import { signIn } from 'next-auth/react';
import Image from 'next/image';

export function LoginScreen() {
  const handleGitHubSignIn = () => {
    signIn('github', { callbackUrl: '/' });
  };

  return (
    <div className="min-h-screen bg-white flex items-center justify-center">
      <div className="text-center max-w-md mx-auto px-4">
        {/* Logo */}
        <div className="mb-8">
          <div className="w-16 h-16 rounded-full overflow-hidden mx-auto mb-4 shadow-md bg-black">
            <Image
              src="/shipsafe-logo.jpg"
              alt="ShipSafe logo"
              width={64}
              height={64}
              className="object-cover w-16 h-16"
              priority
            />
          </div>
          <h1 className="text-2xl font-bold text-black mb-2">ShipSafe</h1>
          <p className="text-gray-600 text-sm">
            Don't let vulnerable code get into production
          </p>
        </div>

        {/* Login Button */}
        <button
          onClick={handleGitHubSignIn}
          className="w-full bg-black hover:bg-gray-800 text-white font-medium py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-3 mb-6"
        >
          <Github className="w-5 h-5" />
          Continue with GitHub
        </button>

        {/* Features */}
        <div className="text-left space-y-4 text-sm text-gray-600">
          <div className="flex items-start gap-3">
            <div className="w-1.5 h-1.5 bg-black rounded-full mt-2 flex-shrink-0"></div>
            <div>
              <p className="text-black font-medium">Connect with GitHub</p>
              <p>Real-Time Scanning to catch security issues before deployment</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-1.5 h-1.5 bg-black rounded-full mt-2 flex-shrink-0"></div>
            <div>
              <p className="text-black font-medium">AI Agent Powered Detection</p>
              <p>AI agents analyze your code with context to identify vulnerabilities instantly</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-1.5 h-1.5 bg-black rounded-full mt-2 flex-shrink-0"></div>
            <div>
              <p className="text-black font-medium">Stop Breaches Early</p>
              <p>Get immediate, actionable feedback to fix security issues before they reach production</p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 text-xs text-gray-500">
          <p>
            By continuing, you agree to our{' '}
            <a href="#" className="text-black hover:underline">Terms of Service</a>{' '}
            and{' '}
            <a href="#" className="text-black hover:underline">Privacy Policy</a>
          </p>
        </div>
      </div>
    </div>
  );
}

