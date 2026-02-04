import { ENV } from '@/lib/env';
import { NextResponse } from 'next/server';
import {isSaneUtf8} from '@/lib/utils';

export async function GET(request: Request) {
  try {
  const VALID = new Set(['aetc', 'jko', 'coursera', 'p2881']);
  const { searchParams } = new URL(request.url);
  const source = searchParams.get('source');
  const target = searchParams.get('target');

  if (!VALID.has(source ?? '') || !VALID.has(target ?? '') || !isSaneUtf8(source ?? '') || !isSaneUtf8(target ?? '')) {
    return NextResponse.json({ error: 'Invalid source or target' }, { status: 400 });
  }
  
  if (!source || !target) {
    return NextResponse.json({ error: 'source and target are required' }, { status: 400 });
  }

  const upstream = new URL(`${ENV.CCV_BASE_URL}/api/mapped-terms`);
  upstream.searchParams.set('source', source);
  upstream.searchParams.set('target', target);

  const resp = await fetch(upstream.toString());

  if (!resp.ok) {
    return NextResponse.json({ error: 'upstream fetch failed' }, { status: resp.status });
  }

  const data = await resp.json();

  return NextResponse.json(data);
} catch (error) {
    console.error('Error in mapped-terms route:', error);
    return NextResponse.json({ error: 'Error fetching mapped terms' }, { status: 500 });  
  }
}