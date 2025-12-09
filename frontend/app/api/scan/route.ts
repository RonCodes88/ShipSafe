import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { repo_url } = body;

    if (!repo_url) {
      return NextResponse.json(
        { success: false, error: 'repo_url is required' },
        { status: 400 }
      );
    }

    // Proxy request to backend (now returns scan_id immediately)
    const response = await fetch(`${BACKEND_URL}/api/scan`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ repo_url }),
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(
        { success: false, error: data.error || 'Failed to start scan' },
        { status: response.status }
      );
    }

    // Backend now returns { success: true, scan_id: "uuid" }
    return NextResponse.json(data);
  } catch (error: any) {
    console.error('Scan API error:', error);

    return NextResponse.json(
      {
        success: false,
        error: error.message || 'An unexpected error occurred',
      },
      { status: 500 }
    );
  }
}
