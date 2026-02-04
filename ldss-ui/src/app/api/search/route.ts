import { NextResponse } from 'next/server';
import { hasNullByte, isSaneUtf8 } from '@/lib/utils';
import { searchCourses } from '@/lib/search';

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const raw = searchParams.get('keyword') ?? '';

  const tooLong      = raw.length >= 250; 
  const badUtf8      = !isSaneUtf8(raw);
  const hasRealNull  = hasNullByte(raw);

  if (tooLong || badUtf8 || hasRealNull) {
    return NextResponse.json({ error: 'Invalid keyword' }, { status: 400 });
  }

  try {
    const results = await searchCourses(raw);
    if (!results || results.length === 0) {
      return NextResponse.json({ error: 'No courses found' }, { status: 404 });
    }
    return NextResponse.json(results);
  } catch (err) {
    console.error('Search failed:', err);
    return NextResponse.json({ error: 'Server error' }, { status: 500 });
  }
}
