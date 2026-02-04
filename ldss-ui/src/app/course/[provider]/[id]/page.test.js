/**
 * @jest-environment jsdom
 */

import { render, screen } from '@testing-library/react';
import React from 'react';

const { default: CourseDetailPage } = require('./page');

jest.mock('next/navigation', () => ({
  notFound: jest.fn(() => {
    throw new Error('not-found');
  }),
}));

// Mock ENV used by the component
jest.mock('@/lib/env', () => ({
  ENV: { CCV_BASE_URL: 'https://mock-api' },
}));

jest.mock('@/lib/utils', () => ({
  isSaneUtf8: jest.fn(),
}));

jest.mock('./CourseDetailClient', () => {
    const CourseDetailClient = (props) => <div data-testid="client">{JSON.stringify(props)}</div>;
    CourseDetailClient.displayName = 'CourseDetailClient';
    return CourseDetailClient;
  });
  
  jest.mock('../../../../../components/Header', () => {
    const Header = () => <div data-testid="header">Header</div>;
    Header.displayName = 'Header';
    return Header;
  });
  
  jest.mock('../../../../../components/Footer', () => {
    const Footer = () => <div data-testid="footer">Footer</div>;
    Footer.displayName = 'Footer';
    return Footer;
  });

describe('CourseDetailPage (server component)', () => {
  let utils;
  let nav;
  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch = jest.fn();

    utils = require('@/lib/utils');
    nav = require('next/navigation');
  });

  afterEach(() => {
    delete global.fetch;
  });

  it('renders Header, CourseDetailClient and Footer when provider/id valid and fetch ok', async () => {
    utils.isSaneUtf8.mockReturnValue(true);

    const mockCourse = { some: 'course-object', title: 'MyCourse' };
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockCourse,
    });

    const element = await CourseDetailPage({ params: Promise.resolve({ provider: 'jko', id: 'C123' }) });

    render(element);

    expect(screen.getByTestId('header')).toBeInTheDocument();
    expect(screen.getByTestId('footer')).toBeInTheDocument();

    const client = screen.getByTestId('client').textContent;
    expect(client).toContain('"initialProvider":"jko"');
    expect(client).toContain('"some":"course-object"');
  });

  it('calls notFound for invalid provider', async () => {
    utils.isSaneUtf8.mockReturnValue(true);

    await expect(
      CourseDetailPage({ params: Promise.resolve({ provider: 'badprovider', id: 'C1' }) })
    ).rejects.toThrow('not-found');

    expect(nav.notFound).toHaveBeenCalled();
  });

  it('calls notFound for invalid id (too long or non-sane)', async () => {
    utils.isSaneUtf8.mockReturnValue(true);
    const longId = 'x'.repeat(251);

    await expect(
      CourseDetailPage({ params: Promise.resolve({ provider: 'jko', id: longId }) })
    ).rejects.toThrow('not-found');

    expect(nav.notFound).toHaveBeenCalled();
  });

  it('calls notFound when fetch returns not ok', async () => {
    utils.isSaneUtf8.mockReturnValue(true);

    global.fetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({ error: 'bad' }),
    });

    await expect(
      CourseDetailPage({ params: Promise.resolve({ provider: 'jko', id: 'C123' }) })
    ).rejects.toThrow('not-found');

    expect(nav.notFound).toHaveBeenCalled();
  });
});
