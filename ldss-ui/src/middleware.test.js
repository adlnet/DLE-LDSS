/**
 * @jest-environment node
 */

import { jwtVerify } from 'jose';
import { middleware } from './middleware';

jest.mock('jose', () => ({
  __esModule: true,
  jwtVerify: jest.fn(),
  createRemoteJWKSet: jest.fn(() => ({})),
}));

const makeReq = (path, headers, origin) => {
  const p = (path == null) ? '/table/courses' : path;
  const o = (origin == null) ? 'http://localhost' : origin;
  const url = new URL(o + p);
  return {
    nextUrl: url,              // minimal NextRequest-like shape
    url: url.toString(),
    headers: new Headers(headers || {}),
  };
};

const makeTraversalReq = (rawPath, headers, origin) => {
  const p = (rawPath == null) ? '/table/../../etc/passwd' : rawPath;
  const o = (origin == null) ? 'http://localhost' : origin;
  return {
    url: o + p,
    nextUrl: { pathname: p, origin: o }, // raw, not normalized
    headers: new Headers(headers || {}),
  };
};

describe('middleware', () => {
  const originalEnv = process.env;
  const originalCrypto = global.crypto;
  const DEFAULT_ALLOWED_GROUPS = ['/Impact Level 2 Authorized', '/Platform One/Products/adl-ousd/LDSS/IL2/roles/USER_STAFF'];
  function mockJwt({ groups = DEFAULT_ALLOWED_GROUPS, username = 'testuser' } = {}) {
    jwtVerify.mockResolvedValue({
      payload: {
        'group-full': groups,
        preferred_username: username,
      },
    });
  }

  beforeEach(() => {
    jest.resetAllMocks();
    process.env = { ...originalEnv, NODE_ENV: 'production' };
    global.fetch = jest.fn(async (u) => {
      if (u.endsWith('/api/busy')) {
        return { status: 200 };
      }
      return { status: 200 };
    });

    Object.defineProperty(global, 'crypto', {
      configurable: true,
      value: { randomUUID: jest.fn(() => 'test-uuid') },
    });
  });

  afterAll(() => {
    process.env = originalEnv;
    Object.defineProperty(global, 'crypto', { configurable: true, value: originalCrypto });
  });

  it('returns 503 when server is busy', async () => {
    (global.fetch).mockResolvedValueOnce({ status: 503 });

    const req = makeReq('/table/data');
    const res = await middleware(req);

    expect(global.fetch).toHaveBeenCalledWith('http://localhost/api/busy', { cache: 'no-store' });
    expect(res.status).toBe(503);
    const txt = await (res).text();
    expect(txt).toContain('too busy');
  });

  it('redirects to /login when token is missing', async () => {
    const req = makeReq('/table/data');
    const res = await middleware(req);

    expect(res.status).toBe(307);
    expect(res.headers.get('location')).toBe('http://localhost/login');
  });

  it('accepts Authorization: Bearer token and allows when groups are sufficient', async () => {
    mockJwt({ username: 'testuser' });

    const req = makeReq('/search/q', { authorization: 'Bearer tok123' });
    const res = await middleware(req);

    expect(jwtVerify).toHaveBeenCalledTimes(1);
    expect(res.status).toBe(200);

    expect(res.headers.get('x-user')).toBe('testuser');
    const nonce = res.headers.get('x-nonce');
    expect(nonce).toBeTruthy();

    const csp = res.headers.get('content-security-policy');
    expect(csp).toBeTruthy();
    expect(csp).toContain(`'nonce-${nonce}'`);

    expect(res.headers.get('cache-control')).toContain('no-cache');
    expect(res.headers.get('pragma')).toBe('no-cache');
    expect(res.headers.get('expires')).toBe('-1');
  });

  it('redirects to /unauthorized when user lacks required groups', async () => {
    mockJwt({ groups: ['USER_STAFF'], username: 'testuser' });

    const req = makeReq('/table/data', { authorization: 'Bearer tok123' });
    const res = await middleware(req);

    expect(res.status).toBe(307);
    expect(res.headers.get('location')).toBe('http://localhost/unauthorized');
  });

  it('redirects to /login when jwtVerify throws', async () => {
    (jwtVerify).mockRejectedValue(new Error('bad token'));

    const req = makeReq('/table/data', { authorization: 'Bearer bad' });
    const res = await middleware(req);

    expect(res.status).toBe(307);
    expect(res.headers.get('location')).toBe('http://localhost/login');
  });

  it('uses alternative header x-istio-jwt-assertion if present', async () => {
    mockJwt({ username: 'alt' });

    const req = makeReq('/table/data', { 'x-istio-jwt-assertion': 'tok-istio' });
    const res = await middleware(req);

    expect(jwtVerify).toHaveBeenCalledWith(
      'tok-istio',
      expect.anything(),
      expect.objectContaining({
        issuer: expect.any(String),
        audience: expect.any(String),
      })
    );
    expect(res.status).toBe(200);
    expect(res.headers.get('x-user')).toBe('alt');
  });

  it('in development, uses DEV_JWT when no header is provided', async () => {
    process.env.NODE_ENV = 'development';
    process.env.DEV_JWT = 'dev-token';
    process.env.JWT_SECRET = 'dev-secret';

    mockJwt({ username: 'devuser' });

    const req = makeReq('/search/x');
    const res = await middleware(req);

    expect(jwtVerify).toHaveBeenCalledWith(
      'dev-token',
      expect.any(Uint8Array),
      expect.any(Object)
    );
    expect(res.status).toBe(200);
    expect(res.headers.get('x-user')).toBe('devuser');
  });
});
