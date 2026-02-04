import { ENV } from '@/lib/env';
import type { AetcCourse, Course, JkoCourse } from '@/app/search/types';

// -------------------- Helper: extract catalog entries --------------------
function extractCatalogList<T extends object>(body: any): T[] {
  if (!body || typeof body !== 'object') return [];

  for (const [key, value] of Object.entries(body)) {
    if (key === '_errors') continue;
    if (Array.isArray(value)) return value as T[];
  }

  return [];
}

export async function searchCourses(keyword: string): Promise<Course[]> {
  const providers = [
    { name: 'aetc', url: `${ENV.CCV_BASE_URL}/api/catalog/all/?provider=aetc` },
    { name: 'jko', url: `${ENV.CCV_BASE_URL}/api/catalog/all/?provider=jko` },
  ] as const;

  const raw = await Promise.all(
    providers.map(async (p) => {
      try {
        const res = await fetch(p.url, { cache: 'no-store' });
        if (!res.ok) throw new Error(`Fetch failed for ${p.name}`);
        const body = await res.json();
        const list = extractCatalogList<AetcCourse | JkoCourse>(body);

        return list.map((item) => ({ ...item, provider: p.name } as Course));
      } catch (err) {
        console.error(`Error fetching courses for ${p.name}:`, err);
        return []; // fail gracefully
      }
    })
  );

  const all = raw.flat();
  const kw = keyword.trim().toLowerCase();

  if (!kw) return all;

  const matchedProvider = providers.find((p) => p.name === kw);
  if (matchedProvider) {
    return all.filter((c) => c.provider === matchedProvider.name);
  }

  return all.filter((c) => {
    const name =
      'course_name' in c
        ? (c.course_name ?? '').toLowerCase()
        : (c.learning_resource_name ?? '').toLowerCase();
    const desc =
      'course_description' in c
        ? (c.course_description ?? '').toLowerCase()
        : (c.learning_resource_description ?? '').toLowerCase();

    return name.includes(kw) || desc.includes(kw);
  });
}
