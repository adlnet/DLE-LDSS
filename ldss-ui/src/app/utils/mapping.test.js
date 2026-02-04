/**
 * @jest-environment jsdom
 */

import { ENV } from '@/lib/env';
import { fetchMappedTerms } from './mapping';

describe('mapping utils', () => {
  const baseUrl = 'https://example.com';
  const source = 'jko';
  const target = 'coursera';

  beforeAll(() => {
    // @ts-ignore - override ENV for test
    ENV.CCV_BASE_URL = baseUrl;
  });

  beforeEach(() => {
    jest.resetAllMocks();
  });

  describe('fetchMappedTerms', () => {
    it('fetches mapped terms successfully', async () => {
      const mockData = [
        {
          source: { alias: 'A', definition: 'Alpha' },
          target: { alias: 'B', definition: 'Beta' },
        },
      ];

      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: async () => mockData,
      });

      const result = await fetchMappedTerms(source, target);

      expect(global.fetch).toHaveBeenCalledWith(
        `${baseUrl}/api/mapped-terms?source=${encodeURIComponent(source)}&target=${encodeURIComponent(target)}`
      );
      expect(result).toEqual(mockData);
    });

    it('throws error when fetch fails', async () => {
      global.fetch = jest.fn().mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Server Error',
      });

      await expect(fetchMappedTerms(source, target)).rejects.toThrow(
        'Failed to fetch mapped terms: 500 Server Error'
      );
    });
  });
});
