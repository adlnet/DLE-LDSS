/**
 * @jest-environment jsdom
 */

import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import CourseDetailPage from './page';
import React from 'react';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useParams: () => ({ courseId: 'abc123' }),
}));

// Mock ENV
jest.mock('@/lib/env', () => ({
  ENV: { CCV_BASE_URL: 'https://mock-api' },
}));

// Mock child components 
jest.mock('../../../../components/Dropdown', () => {
  const PropTypes = require('prop-types');

  const Dropdown = (props) => (
    <div data-testid="dropdown">
      <button onClick={() => props.onChange({ id: 'coursera' })}>Change</button>
      <span>{props.value}</span>
    </div>
  );
  Dropdown.displayName = 'Dropdown';
  Dropdown.propTypes = {
    onChange: PropTypes.func.isRequired,
    value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  };
  return Dropdown;
});

jest.mock('../../../../components/Footer', () => {
  const Footer = () => <div>Footer</div>;
  Footer.displayName = 'Footer';
  return Footer;
});

jest.mock('../../../../components/Header', () => {
  const Header = () => <div>Header</div>;
  Header.displayName = 'Header';
  return Header;
});

beforeEach(() => {
  jest.clearAllMocks();
  global.fetch = jest.fn();
});

describe('CourseDetailPage', () => {
  it('renders loading state initially', () => {
    render(<CourseDetailPage />);
    expect(screen.getByText(/Loading/i)).toBeInTheDocument();
  });

  it('renders "Course data not available" if API returns empty', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [], // no mappings
    });
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ hits: [] }),
    });

    render(<CourseDetailPage />);

    const msg = await screen.findByText(/Course data not available/i);
    expect(msg).toBeInTheDocument();
  });

  it('renders course data when API responds', async () => {
    // 1) mapping fetch
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [
        {
          source: { alias: 'Course Code', definition: 'Course Code' },
          target: { alias: 'Código', definition: 'Código' },
          relationship: true,
        },
      ],
    });

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        hits: [
          {
            Course: {
              CourseTitle: 'Mock Course',
              CourseCode: 'C123',
              CourseShortDescription: 'A test course',
              CourseProviderName: 'JKO',
              instructor: 'Jane Doe',
              delivery: 'Online',
              details: [{ title: 'Detail 1', content: 'Detail content' }],
              url: 'http://example.com',
            },
            Course_Instance: {
              Thumbnail: '/test.png',
              StartDate: '2025-01-01',
              EndDate: '2025-02-01',
            },
            Supplemental_Ledger: { Instance: 1 },
          },
        ],
      }),
    });

    render(<CourseDetailPage />);

    expect(await screen.findByText('Mock Course')).toBeInTheDocument();
    expect(screen.getByText(/C123/)).toBeInTheDocument();
    expect(screen.getByText(/A test course/)).toBeInTheDocument();
    expect(screen.getByText(/Jane Doe/)).toBeInTheDocument();
    expect(screen.getByText(/Online/)).toBeInTheDocument();
    expect(screen.getByText(/Detail content/)).toBeInTheDocument();
  });

  it('toggles language button', async () => {
    // mapping fetch
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [
        {
          source: { alias: 'Provider', definition: 'Provider' },
          target: { alias: 'Proveedor', definition: 'Proveedor' },
          relationship: true,
        },
      ],
    });

    // course data fetch
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        hits: [
          {
            Course: {
              CourseTitle: 'Mock Course',
              CourseCode: 'C123',
              CourseShortDescription: 'desc',
              CourseProviderName: 'JKO',
              instructor: 'Jane Doe',
              delivery: 'Online',
              details: [],
              url: '',
            },
            Course_Instance: {
              Thumbnail: null,
              StartDate: '2025-01-01',
              EndDate: '2025-02-01',
            },
            Supplemental_Ledger: { Instance: 1 },
          },
        ],
      }),
    });

    render(<CourseDetailPage />);

    await screen.findByText('Mock Course');

    const buttons = await screen.findAllByRole('button');
    const languageToggle = buttons[buttons.length - 1];

    fireEvent.click(languageToggle);

    await waitFor(() => {
      expect(screen.getByText(/Target/i)).toBeInTheDocument();
    });
  });
});
