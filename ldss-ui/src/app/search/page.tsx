'use client';

import { Suspense, useEffect, useMemo, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import type { Course } from './types';

export const dynamic = 'force-dynamic'; // optional: avoids static prerender quirks

function hasControlChars(s: string): boolean {
  for (let i = 0; i < s.length; i++) {
    const code = s.charCodeAt(i);
    if (code <= 0x1F || code === 0x7F || (code >= 0x80 && code <= 0x9F)) {
      return true;
    }
  }
  return false;
}

export default function SearchPage() {
  return (
    <Suspense fallback={<div className="max-w-4xl mx-auto py-8">Loading…</div>}>
      <SearchContent />
    </Suspense>
  );
}

function SearchContent() {
  const router = useRouter();
  const sp = useSearchParams();

  const raw = sp.get('keyword') ?? '';
  const keyword = useMemo(() => raw.normalize('NFC').trim(), [raw]);

  const [results, setResults] = useState<Course[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState('');

  // UX guard (server/API still does real validation)
  useEffect(() => {
    if (raw.length > 250 || hasControlChars(raw) || /%00/i.test(raw)) {
      router.replace('/?err=invalid');
    }
  }, [raw, router]);

  // Fetch from your API (server-side validation + 400s)
  useEffect(() => {
    let cancelled = false;

    async function run() {
      setLoading(true);
      setErr('');
      try {
        const res = await fetch(
          `/api/search?keyword=${encodeURIComponent(keyword)}`,
          { cache: 'no-store' }
        );
        if (!res.ok) {
          const body = await res.json().catch(() => ({}));
          throw new Error(body?.error || 'Invalid keyword');
        }
        const data = (await res.json()) as Course[];
        if (!cancelled) setResults(data);
      } catch (e: any) {
        if (!cancelled) setErr(e?.message || 'Something went wrong');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    // Call API even for empty keyword if you want “All Courses”
    run();
    return () => {
      cancelled = true;
    };
  }, [keyword]);

  return (
    <main className="max-w-4xl mx-auto py-8">
      <h1 className="text-2xl font-bold mb-4">
        {keyword ? `Results for “${keyword}”` : 'All Courses'}
      </h1>

      {loading && <p className="text-gray-600">Loading…</p>}
      {err && <p className="text-red-600">{err}</p>}

      {!loading && !err && results.length === 0 && (
        <p className="text-gray-600">No courses found.</p>
      )}

      {!loading && !err && results.length > 0 && (
        <ul className="space-y-4">
          {results.map((c) => {
            const title =
              'course_name' in c ? c.course_name : c.learning_resource_name;
            const href = `/course/${c.provider}/${c.id}`;
            return (
              <li key={`${c.provider}-${c.id}`} className="p-4 border rounded">
                <Link href={href} className="text-lg font-medium hover:underline">
                  {title}
                </Link>
                <p className="text-sm text-gray-700 mt-1">
                  {(
                    'course_description' in c
                      ? c.course_description
                      : c.learning_resource_description
                  ) ?? 'No description.'}
                </p>
                <span className="inline-block mt-2 px-2 py-0.5 bg-blue-100 text-blue-800 text-xs rounded">
                  {c.provider.toUpperCase()}
                </span>
              </li>
            );
          })}
        </ul>
      )}
    </main>
  );
}
