export async function GET(request: Request) {
  const headersObj: Record<string, string> = {};

  for (const [key, value] of request.headers) {
    headersObj[key] = value;
    console.log(`Header "${key}" = "${value}"`);
  }

  // Highlight potential Istio-injected headers
  const relevantHeaders = ['authorization', 'x-istio-jwt-assertion', 'sec-istio-auth-userinfo'];
  relevantHeaders.forEach(name => {
    const val = request.headers.get(name);
    console.log(`${name}:`, val ?? '(not present)');
    if (val) headersObj[name] = val;
  });

  return new Response(JSON.stringify(headersObj), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });
}