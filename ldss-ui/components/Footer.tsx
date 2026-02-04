'use strict';

import { makeExternalLinks } from './utils';
import React from 'react';

export default function Footer({ }) {
  const leftLinks = [
    { name: 'DOD Home Page', url: 'https://www.defense.gov/', number: 1 },
    { name: 'About ADL', url: 'https://adlnet.gov/about/', number:2 },
    { name: 'Web Policy', url: 'https://dodcio.defense.gov/DoD-Web-Policy/', number:3 },
  ];
  const rightLinks = [
    {
      name: 'Privacy',
      url: 'https://dodcio.defense.gov/Home/Privacy-Policy.aspx', number:4
    },
    { name: 'Contact US', url: 'https://dodcio.defense.gov/Contact/', number:5 },
  ];


  return (
    <div className='mt-10 bottom-0 bg-opacity-90 w-full mx-auto z-50'>
      <nav className={'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 border-t'}>
        <div className={'w-full py-4 inline-flex items-center justify-between'}>
          <div className={'flex items-center gap-4'}>
            {makeExternalLinks(leftLinks)}
          </div>
          <div className={'flex items-right gap-4'}>
            {makeExternalLinks(rightLinks)}
          </div>
        </div>
      </nav>
    </div>
  );
}

