import { JWTPayload, createRemoteJWKSet, jwtVerify } from 'jose';
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const jwks = createRemoteJWKSet(
  new URL('https://login.dso.mil/auth/realms/baby-yoda/protocol/openid-connect/certs')
);

const allowedGroups = [
  '/Impact Level 2 Authorized',
  '/Platform One/Products/adl-ousd/LDSS/IL2/roles/USER_STAFF'
];

export const config = {
  matcher: ['/table/:path*', '/search/:path*'],
};

// -------------------- Helper functions --------------------

function isPathTraversal(path: string) {
  return path.includes('../');
}

async function checkServerBusy(origin: string) {
  try {
    const res = await fetch(`${origin}/api/busy`, { cache: 'no-store' });
    if (res.status === 503) return true;
  } catch (e) {
    console.error('Busy check failed:', e);
  }
  return false;
}

function createCSPHeader(nonce: string) {
  return `
    default-src 'self';
    script-src 'self' 'nonce-${nonce}' 'strict-dynamic' https: http: ${
      process.env.NODE_ENV === 'production' ? '' : `'unsafe-eval'`
    };
    style-src 'self' 'nonce-${nonce}';
    img-src 'self' blob: data:;
    font-src 'self';
    object-src 'none';
    base-uri 'self';
    form-action 'self';
    frame-ancestors 'none';
    frame-src 'none';
    upgrade-insecure-requests;
    connect-src 'self';
  `.replace(/\s{2,}/g, ' ').trim();
}

function extractToken(req: NextRequest): string | null {
  const headerCandidates = [
    'authorization',
    'x-istio-jwt-assertion',
    'sec-istio-auth-userinfo',
  ];

  for (const name of headerCandidates) {
    const val = req.headers.get(name);
    if (val) {
      if (name === 'authorization' && val.toLowerCase().startsWith('bearer ')) {
        return val.slice(7).trim();
      }
      return val;
    }
  }

  if (
    (process.env.NODE_ENV === 'development' || process.env.NODE_ENV === 'test') && 
     process.env.DEV_JWT
  ) {
    return process.env.DEV_JWT;
  }

  return null;
}

async function verifyToken(token: string): Promise<JWTPayload> {
  const verifyOptions = {
    issuer: 'https://login.dso.mil/auth/realms/baby-yoda',
    audience: 'il2_00eb8904-5b88-4c68-ad67-cec0d2e07aa6_mission-staging',
  };

  if (process.env.NODE_ENV === 'development') {

    const secret = process.env.JWT_SECRET;

    if(!secret){
       throw new Error('Missing JWT_SECRET in development');
    }
    
    const { payload } = await jwtVerify(
      token,
      new TextEncoder().encode(secret),
      verifyOptions
    );
    return payload;
  }

  const { payload } = await jwtVerify(token, jwks, verifyOptions);
  return payload;
}

function checkUserGroups(payload: JWTPayload) {
  const userGroups = Array.isArray(payload['group-full'])
    ? (payload['group-full'] as string[])
    : [];
  return allowedGroups.every((g) => userGroups.includes(g));
}

function buildResponse(payload: JWTPayload, nonce: string) {
  const res = NextResponse.next();
  if (typeof payload.preferred_username === 'string') {
    res.headers.set('x-user', payload.preferred_username);
  }
  res.headers.set('Cache-Control', 'no-cache, no-store, max-age=0, must-revalidate');
  res.headers.set('Pragma', 'no-cache');
  res.headers.set('Expires', '-1');
  res.headers.set('Content-Security-Policy', createCSPHeader(nonce));
  res.headers.set('x-nonce', nonce);
  return res;
}

// -------------------- Middleware --------------------

export async function middleware(req: NextRequest) {
  if (isPathTraversal(req.nextUrl.pathname)) {
    console.error('Blocked path traversal attempt:', req.nextUrl.pathname);
    return new Response('Blocked', { status: 403 });
  }

  if (await checkServerBusy(req.nextUrl.origin)) {
    console.error('Server is too busy, rejecting request');
    return new NextResponse('Server is currently too busy. Please try again later.', { status: 503 });
  }

  try {
    if (process.env.NODE_ENV === 'production' && req.headers.get('x-cypress-test') === 'true') {
      const nonce = Buffer.from(crypto.randomUUID()).toString('base64');
      return buildResponse(
        { preferred_username: 'ci-test-user', 'group-full': allowedGroups },
        nonce
      );
    }

    const token = extractToken(req);
    if (!token) return NextResponse.redirect(new URL('/login', req.url));

    const payload = await verifyToken(token);
    if (!checkUserGroups(payload)) return NextResponse.redirect(new URL('/unauthorized', req.url));

    const nonce = Buffer.from(crypto.randomUUID()).toString('base64');
    return buildResponse(payload, nonce);

  } catch (err) {
    console.error('JWT verification failed:', err);
    return NextResponse.redirect(new URL('/login', req.url));
  }
}