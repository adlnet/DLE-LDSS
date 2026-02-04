import { GET } from './route'; // adjust path if needed

describe('GET handler', () => {
  afterEach(() => {
    jest.resetAllMocks();
  });

  it('returns 200 on successful fetch', async () => {
    const mockData = [{ id: 1, name: 'Test Instance' }];
    global.fetch = jest.fn(() =>
        Promise.resolve({
            ok: true,
            status: 200,
            json: async () => mockData,
            headers: {
              get: (header) => {
                if (header.toLowerCase() === 'content-type') {
                  return 'application/json';
                }
                return null;
              },
            },
        })
      );

    const response = await GET();
    expect(response.status).toBe(200);
    const body = await response.json();
    expect(body).toEqual(mockData);
    expect(response.headers.get('content-type')).toBe('application/json');
  });

  it('returns 502 on fetch with !ok', async () => {
    (global.fetch).mockResolvedValue({
      ok: false,
      status: 500,
    });

    const response = await GET();
    expect(response.status).toBe(502);
    const body = await response.json();
    expect(body).toEqual({ error: 'External API failure' });
  });

  it('returns 502 on fetch error', async () => {
    (global.fetch).mockRejectedValue(new Error('Network error'));

    const response = await GET();
    expect(response.status).toBe(502);
    const body = await response.json();
    expect(body).toEqual({ error: 'Unable to reach external API' });
  });
});
