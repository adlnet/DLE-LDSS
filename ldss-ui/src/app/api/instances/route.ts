import { ENV } from '@/lib/env';

export async function GET() {
  try {
    const resp = await fetch(`${ENV.CCV_BASE_URL}/api/instances`);
    if (!resp.ok) {
      console.error('[api/instances] external returned', resp.status);
      return new Response(
        JSON.stringify({ error: 'External API failure' }),
        {
          status: 502,
          headers: { 'Content-Type': 'application/json' },
        }
      );
    }
    const data = await resp.json();
    return new Response(JSON.stringify(data), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    }); // so its throwing an error and coming here instead of new response
  } catch (err) {
    console.error('[api/instances] fetch error:', err);
    return new Response(
      JSON.stringify({ error: 'Unable to reach external API' }),
      {
        status: 502,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }
}
