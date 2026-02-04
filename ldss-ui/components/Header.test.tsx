// __tests__/Header.test.tsx

import { Button } from '../components/Header';
import { render, screen } from '@testing-library/react';
import Header from '../components/Header';
import React from 'react';

import '@testing-library/jest-dom';
import { usePathname } from 'next/navigation';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  usePathname: jest.fn(),
}));

// Make sure button componenet renders properly. 
describe('Button Subcomponent render', () => {

    it('applies active class when pathname matches', () => {
      (usePathname as jest.Mock).mockReturnValue('/table');
  
      render(<Button data={{ label: 'Table', path: '/table' }} />);
      const link = screen.getByRole('link', { name: 'Table' });
  
      expect(link).toHaveClass('font-bold');
      expect(link).toBeInTheDocument;
    });
  
    it('does not apply active class when pathname does not match', () => {
      (usePathname as jest.Mock).mockReturnValue('/');
  
      render(<Button data={{ label: 'Table', path: '/table' }} />);
      const link = screen.getByRole('link', { name: 'Table' });
  
      expect(link).not.toHaveClass('font-bold');
      expect(link).toBeInTheDocument;
    });
  });

describe('Header Component Rendering', () => {
  it('renders the header container with key layout classes', () => {
    const { container } = render(<Header />);
    const header = container.querySelector('header');
    expect(header).toBeInTheDocument();
    expect(header).toHaveClass('bg-white', 'w-full', 'shadow', 'z-50');
  });

  it('renders the nav with proper classes and aria-label', () => {
    const { container } = render(<Header />);
    const nav = container.querySelector('nav');
    expect(nav).toBeInTheDocument();
    expect(nav).toHaveAttribute('aria-label', 'Top');
    expect(nav).toHaveClass('max-w-7xl', 'mx-auto');
  });

  it('renders the layout wrapper with key Tailwind classes', () => {
    const { container } = render(<Header />);
    const layoutDiv = container.querySelector('nav > div');
    expect(layoutDiv).toHaveClass('w-full');
    expect(layoutDiv).toHaveClass('justify-between');
  });

  it('renders both left and right containers inside the layout wrapper', () => {
    const { container } = render(<Header />);
    const layoutDiv = container.querySelector('nav > div');
    const childDivs = layoutDiv?.querySelectorAll('div');
    expect(childDivs?.length).toBe(2);
  });

  it('renders logo inside a link to home', () => {
    render(<Header />);
    const logoLink = screen.getByTitle(/home/i);
    expect(logoLink).toBeInTheDocument();
    expect(logoLink).toHaveAttribute('href', '/');
    const logoImage = screen.getByAltText(/logo/i);
    expect(logoImage).toBeInTheDocument();
  });

  it('renders Home and Table buttons with correct links', () => {
    render(<Header />);
    const homeLink = screen.getByRole('link', { name: 'Home' });
    const tableLink = screen.getByRole('link', { name: 'Table' });
    expect(homeLink).toHaveAttribute('href', '/');
    expect(tableLink).toHaveAttribute('href', '/table');
  });

  it('wraps menu items inside a flex container with gap-2', () => {
    const { container } = render(<Header />);
    const menuContainer = container.querySelector('div.flex.items-center.gap-2');
    expect(menuContainer).toBeInTheDocument();
  });

  it('renders the right container for user auth buttons or user menu', () => {
    const { container } = render(<Header />);
    const rightContainer = container.querySelector('div.flex.items-center.space-x-4');
    expect(rightContainer).toBeInTheDocument();
  });
});

describe('Header Component - User Authentication Display', () => {
  it('shows login and register links when user is false', () => {
    render(<Header user={false} />);
    expect(screen.getByRole('link', { name: /sign in/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /sign up/i })).toBeInTheDocument();
  });

  it('does not show login/register when user is true', () => {
    render(<Header user={true} />);
    expect(screen.queryByRole('link', { name: /sign in/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('link', { name: /sign up/i })).not.toBeInTheDocument();
  });
});

describe('Header Navigation Active State', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('highlights the Home button when pathname is "/"', () => {
    (usePathname as jest.Mock).mockReturnValue('/');
    render(<Header />);
    expect(screen.getByRole('link', { name: 'Home' })).toHaveClass('font-bold');
    expect(screen.getByRole('link', { name: 'Table' })).not.toHaveClass('font-bold');
  });

  it('highlights the Table button when pathname is "/table"', () => {
    (usePathname as jest.Mock).mockReturnValue('/table');
    render(<Header />);
    expect(screen.getByRole('link', { name: 'Table' })).toHaveClass('font-bold');
    expect(screen.getByRole('link', { name: 'Home' })).not.toHaveClass('font-bold');
  });
});
