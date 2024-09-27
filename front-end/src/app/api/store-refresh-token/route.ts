import { NextResponse, NextRequest } from 'next/server';
import { serialize } from 'cookie';

export async function POST(req: NextRequest) {
//   const allowedIP = '123.456.789.0'; // Replace with your server's IP address

//   // Restrict access based on IP address
//   const clientIP = req.headers.get('x-forwarded-for') || req.ip;
//   if (clientIP !== allowedIP) {
//     return NextResponse.json({ message: 'Forbidden' }, { status: 403 });
//   }

  const { refresh_token } = await req.json();

  if (!refresh_token) {
    return NextResponse.json({ message: 'Refresh token is required' }, { status: 400 });
  }

  // Set HttpOnly cookie for the refresh token
  const cookie = serialize('refreshToken', refresh_token, {
    httpOnly: true,
    secure: process.env.NODE_ENV !== 'development',
    maxAge: 60 * 60 * 24 * 30, // 30 days
    path: '/',
  });

  const res = NextResponse.json({ message: 'Refresh token stored successfully' });
  res.headers.set('Set-Cookie', cookie);
  return res;
}
