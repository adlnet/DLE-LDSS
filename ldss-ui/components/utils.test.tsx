import { makeExternalLinks } from './utils';
import { render, screen } from '@testing-library/react';
import React from 'react';

describe('makeExternalLinks', () => {
  const mockLinks = [
    { name: 'Test Link 1', url: 'https://example.com/1', number: 1 },
    { name: 'Test Link 2', url: 'https://example.com/2', number: 2 },
  ];

  it('renders links with a className applied', () => {
    render(<>{makeExternalLinks(mockLinks)}</>);

    const link1 = screen.getByRole('link', { name: 'Test Link 1' });
    const link2 = screen.getByRole('link', { name: 'Test Link 2' });

    expect(link1).toHaveAttribute('class');
    expect(link1.getAttribute('class')).toContain('text-center text-gray-500 text-base p-1 hover:text-gray-900 h-auto hover:text-shadow-md transform transition-all duration-75 ease-in-out');
    expect(link1).toHaveAttribute('href', 'https://example.com/1')

    expect(link2).toHaveAttribute('class');
    expect(link2.getAttribute('class')).toContain('text-center text-gray-500 text-base p-1 hover:text-gray-900 h-auto hover:text-shadow-md transform transition-all duration-75 ease-in-out');
    expect(link2).toHaveAttribute('href', 'https://example.com/2');


    });
});
