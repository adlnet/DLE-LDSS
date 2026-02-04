'use strict';


import React, { JSX } from 'react';

type Link = {
  number: React.Key;
  url: string;
  name: React.ReactNode;
};

export function makeExternalLinks(links: Link[]): JSX.Element[] {
  return links.map((link) => (
    <a
      key={link.number}
      className='text-center text-gray-500 text-base p-1 hover:text-gray-900 h-auto hover:text-shadow-md transform transition-all duration-75 ease-in-out'
      href={link.url}
    >
      {link.name}
    </a>
  ));
}
