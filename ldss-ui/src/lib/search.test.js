/**
 * @jest-environment jsdom
 */

import { ENV } from '@/lib/env';
import { searchCourses } from './search';

describe('searchCourses', () => {
  const baseUrl = 'https://example.com';

  beforeAll(() => {
    // Override ENV for tests
    // @ts-ignore
    ENV.CCV_BASE_URL = baseUrl;
  });

  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('fetches from both providers and merges results', async () => {
    const aetcData = {
      aetc: [
        { id: '1', course_name: 'React Basics', course_description: 'Learn React' },
      ],
    };
    const jkoData = {
      jko: [
        { id: '2', learning_resource_name: 'Vue Intro', learning_resource_description: 'Vue 101' },
      ],
    };

    global.fetch = jest
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => aetcData,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => jkoData,
      });

    const results = await searchCourses('react');

    expect(global.fetch).toHaveBeenCalledTimes(2);
    expect(global.fetch).toHaveBeenCalledWith(
      `${baseUrl}/api/catalog/all/?provider=aetc`,
      { cache: 'no-store' }
    );
    expect(global.fetch).toHaveBeenCalledWith(
      `${baseUrl}/api/catalog/all/?provider=jko`,
      { cache: 'no-store' }
    );

    // Should merge results and tag provider
    expect(results).toEqual([
      {
        id: '1',
        course_name: 'React Basics',
        course_description: 'Learn React',
        provider: 'aetc',
      },
    ]);
  });

  it('filters by keyword in name or description (case-insensitive)', async () => {
    const aetcData = {
      aetc: [
        { id: '1', course_name: 'Java Basics', course_description: 'Learn Java' },
      ],
    };
    const jkoData = {
      jko: [
        { id: '2', learning_resource_name: 'Vue Intro', learning_resource_description: 'Vue 101' },
      ],
    };

    global.fetch = jest
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => aetcData,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => jkoData,
      });

    const results = await searchCourses('vue');

    expect(results).toEqual([
      {
        id: '2',
        learning_resource_name: 'Vue Intro',
        learning_resource_description: 'Vue 101',
        provider: 'jko',
      },
    ]);
  });

  it('returns empty array if no matches', async () => {
    const aetcData = { aetc: [] };
    const jkoData = { jko: [] };

    global.fetch = jest
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => aetcData,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => jkoData,
      });

    const results = await searchCourses('python');
    expect(results).toEqual([]);
  });

  it('handles null/undefined descriptions gracefully', async () => {
    const aetcData = {
      aetc: [
        { id: '1', course_name: 'Node.js', course_description: null },
      ],
    };
    const jkoData = {
      jko: [
        { id: '2', learning_resource_name: 'Angular', learning_resource_description: undefined },
      ],
    };

    global.fetch = jest
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => aetcData,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => jkoData,
      });

    const results = await searchCourses('node');

    expect(results).toEqual([
      {
        id: '1',
        course_name: 'Node.js',
        course_description: null,
        provider: 'aetc',
      },
    ]);
  });
});
