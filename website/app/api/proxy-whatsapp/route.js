import { NextResponse } from 'next/server';

export async function POST(request) {
  const body = await request.json();
  const response = await fetch('http://35.230.12.61:5000/api/whatsapp_api/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  const data = await response.json();
  return NextResponse.json(data, { status: response.status });
}

export async function GET(request) {
  const response = await fetch('http://35.230.12.61:5000/api/whatsapp_api/');
  const data = await response.json();
  return NextResponse.json(data, { status: response.status });
}
