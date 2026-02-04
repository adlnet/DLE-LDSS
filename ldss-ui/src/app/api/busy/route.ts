import toobusy from 'toobusy-js';

export async function GET() {
  if (toobusy()) {
    return new Response('Server busy', { status: 503 });
  }
  return new Response('OK');
}