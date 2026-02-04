// __tests__/Footer.test.tsx

import { render, screen } from '@testing-library/react';
import Footer from '../components/Footer';
import React from 'react';

describe('Footer Component', () => {

    let container: HTMLElement;  // declare container here so all tests can use it

  
    beforeEach(() => {

        const renderResult = render(<Footer />);

        container = renderResult.container;

    });

  it('renders all left-side links with correct names and roles', () => {
    expect(screen.getByRole('link', { name: 'DOD Home Page' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'About ADL' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Web Policy' })).toBeInTheDocument();
  });

  it('renders all right-side links with correct names and roles', () => {
    expect(screen.getByRole('link', { name: 'Privacy' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Contact US' })).toBeInTheDocument();
  });

  it('links point to the correct URLs', () => {
    expect(screen.getByRole('link', { name: 'DOD Home Page' })).toHaveAttribute(
      'href',
      'https://www.defense.gov/'
    );
    expect(screen.getByRole('link', { name: 'About ADL' })).toHaveAttribute(
      'href',
      'https://adlnet.gov/about/'
    );
    expect(screen.getByRole('link', { name: 'Web Policy' })).toHaveAttribute(
      'href',
      'https://dodcio.defense.gov/DoD-Web-Policy/'
    );
    expect(screen.getByRole('link', { name: 'Privacy' })).toHaveAttribute(
      'href',
      'https://dodcio.defense.gov/Home/Privacy-Policy.aspx'
    );
    expect(screen.getByRole('link', { name: 'Contact US' })).toHaveAttribute(
      'href',
      'https://dodcio.defense.gov/Contact/'
    );
  });
  it('renders the outer div with key layout classes', () => {
    const outer = container.querySelector('div');
    expect(outer).toHaveClass('w-full');
    expect(outer).toHaveClass('mx-auto');
  });

  it('renders the nav with key layout classes', () => {
    const nav = container.querySelector('nav');
    expect(nav).toHaveClass('max-w-7xl');
    expect(nav).toHaveClass('border-t');

  });

  it('renders the middle layout container with key layout classes', () => {
    const middleDiv = container.querySelector('nav > div');
    expect(middleDiv).toHaveClass('w-full');
    expect(middleDiv).toHaveClass('inline-flex');
    expect(middleDiv).toHaveClass('justify-between');
  });
  
  it('renders left and right link containers inside the layout div', () => {
    const layoutDiv = container.querySelector('nav > div');
    const childDivs = layoutDiv?.querySelectorAll('div');
  
    expect(childDivs?.length).toBe(2); // left and right containers
  });
  
  it('renders the left links container with key layout classes', () => {
    const leftLinksDiv = container.querySelectorAll('div.flex.items-center.gap-4')[0];
    expect(leftLinksDiv).toHaveClass('flex');
    expect(leftLinksDiv).toHaveClass('items-center');
  });
  

  it('renders the right links container with key layout classes', () => {
    const rightLinksDiv = container.querySelectorAll('div.flex.items-right.gap-4')[0];
    expect(rightLinksDiv).toHaveClass('flex');
    expect(rightLinksDiv).toHaveClass('items-right');
  });
  
  
});
 