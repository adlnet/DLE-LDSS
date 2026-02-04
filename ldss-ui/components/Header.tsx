'use client';

import { usePathname } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';
import React from 'react';
import logo from '../public/logo.png';

const menuItems = [
  { label: 'Home', path: '/' },
  { label: 'Table', path: '/table' },
];

export function Button({ data }: { data: { label: string; path: string } }) {
  const pathname = usePathname();
  const isActive = data.path === pathname;
  return (
    <Link
      href={data.path}
      passHref
      className={`px-1 transition-all duration-100 border-b-2 ${
        isActive
          ? 'font-bold text-gray-800 border-gray-800 hover:text-gray-900'
          : 'border-transparent text-gray-500 hover:text-gray-900'
      }`}
    >
      {data.label}
    </Link>
  );
}

export default function Header({ user = true }: { user?: boolean }) {

  return (
    <header className="bg-white w-full shadow z-50">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8" aria-label="Top">
        <div className="w-full py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Link
              href="/"
              passHref
              title="home"
              className="cursor-pointer inline-block"
            >
              <Image src={logo} height={60} width={60} alt="Logo" />
            </Link>
            {menuItems.map((item) => (
              <Button key={item.label} data={item} />
            ))}
          </div>
          <div className="flex items-center space-x-4">
            {!user ? (
              <>
                <Link
                  href="/login"
                  className="bg-blue-500 py-2 px-4 rounded text-white hover:opacity-90 shadow transition-all duration-100 font-semibold"
                >
                  Sign in
                </Link>
                <Link
                  href="/register"
                  className="bg-blue-300 py-2 px-4 rounded text-white hover:opacity-90 shadow transition-all duration-100 font-semibold"
                >
                  Sign up
                </Link>
              </>
            ) : (
              <>
                {/* Your user menu here */}
              </>
            )}
          </div>
        </div>
      </nav>
    </header>
  );
}
