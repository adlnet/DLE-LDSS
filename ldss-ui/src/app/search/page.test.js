/**
 * @jest-environment jsdom
 */

import { render, screen, waitFor } from '@testing-library/react';
import { useSearchParams } from 'next/navigation';
import React from 'react';
import SearchPage from './page';

// Mock router + search params
const mockReplace = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: () => ({ replace: mockReplace }),
  useSearchParams: jest.fn(),
}));

// Mock fetch
global.fetch = jest.fn();

function setSearchParams(params) {
  (useSearchParams).mockReturnValue({
    get: (key) => params[key] ?? null,
  });
}

describe('SearchPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading then no courses found', async () => {
    setSearchParams({ keyword: '' });

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [],
    });

    render(<SearchPage />);

    expect(screen.getByText(/Loading/i)).toBeInTheDocument();

    await waitFor(() =>
      expect(screen.getByText(/No courses found/i)).toBeInTheDocument()
    );
  });

  it('renders error message if fetch fails', async () => {
    setSearchParams({ keyword: 'test' });

    fetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ error: 'Invalid keyword' }),
    });

    render(<SearchPage />);

    await waitFor(() =>
      expect(screen.getByText(/Invalid keyword/i)).toBeInTheDocument()
    );
  });

  it('renders results when fetch returns courses', async () => {
    setSearchParams({ keyword: 'python' });

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [
        {
          id: '1',
          provider: 'jko',
          course_name: 'Intro to Python',
          course_description: 'Learn Python basics',
        },
      ],
    });

    render(<SearchPage />);

    expect(await screen.findByText(/Intro to Python/i)).toBeInTheDocument();
    expect(screen.getByText(/Learn Python basics/i)).toBeInTheDocument();
    expect(screen.getByText(/JKO/i)).toBeInTheDocument();
  });

  it('redirects to /?err=invalid if keyword is invalid', () => {
    // keyword with control char
    setSearchParams({ keyword: '\x01bad' });

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [],
    });

    render(<SearchPage />);

    expect(mockReplace).toHaveBeenCalledWith('/?err=invalid');
  });
});