/**
 * @jest-environment node
 */

import { GET } from './route';
import { hasNullByte, isSaneUtf8 } from '@/lib/utils';
import { searchCourses } from '@/lib/search';

// Mocks
jest.mock('@/lib/utils', () => ({
  hasNullByte: jest.fn(),
  isSaneUtf8: jest.fn(),
}));

jest.mock('@/lib/search', () => ({
  searchCourses: jest.fn(),
}));

const createMockRequest = (keyword) => {
  const url = new URL('http://localhost/api/courses');
  if (keyword !== undefined) {
    url.searchParams.set('keyword', keyword);
  }
  return new Request(url.toString());
};

describe('API /api/courses GET', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    (isSaneUtf8).mockReturnValue(true);
    (hasNullByte).mockReturnValue(false);
  });

  it('returns 400 if keyword is too long', async () => {
    const longKeyword = 'x'.repeat(300);
    const req = createMockRequest(longKeyword);

    const res = await GET(req);
    const data = await res.json();

    expect(res.status).toBe(400);
    expect(data.error).toBe('Invalid keyword');
  });

  it('returns 400 if keyword has invalid UTF-8', async () => {
    (isSaneUtf8).mockReturnValue(false);
    const req = createMockRequest('badutf8');

    const res = await GET(req);
    const data = await res.json();

    expect(res.status).toBe(400);
    expect(data.error).toBe('Invalid keyword');
  });

  it('returns 400 if keyword has null byte', async () => {
    (hasNullByte).mockReturnValue(true);
    const req = createMockRequest('abc\0def');

    const res = await GET(req);
    const data = await res.json();

    expect(res.status).toBe(400);
    expect(data.error).toBe('Invalid keyword');
  });

  it('returns 404 if no results are found', async () => {
    (searchCourses).mockResolvedValue([]);
    const req = createMockRequest('history');

    const res = await GET(req);
    const data = await res.json();

    expect(res.status).toBe(404);
    expect(data.error).toBe('No courses found');
  });

  it('returns 200 with results when courses are found', async () => {
    const fakeResults = [{ id: '1', title: 'Course 1' }];
    (searchCourses).mockResolvedValue(fakeResults);
    const req = createMockRequest('math');

    const res = await GET(req);
    const data = await res.json();

    expect(res.status).toBe(200);
    expect(data).toEqual(fakeResults);
  });

  it('returns 200 with results even if keyword is empty string', async () => {
    const fakeResults = [{ id: '2', title: 'Course 2' }];
    (searchCourses).mockResolvedValue(fakeResults);
    const req = createMockRequest('');

    const res = await GET(req);
    const data = await res.json();

    expect(res.status).toBe(200);
    expect(data).toEqual(fakeResults);
  });
});
