import { ENV } from '@/lib/env';
import { isSaneUtf8 } from '@/lib/utils';
import { notFound } from 'next/navigation';
import CourseDetailClient from './CourseDetailClient';
import Footer from '../../../../../components/Footer';
import Header from '../../../../../components/Header';
import React from 'react';

type DetailParams = Promise<{
  provider: string
  id: string
}>

export default async function CourseDetailPage({
  params,
}: Readonly<{
  params: DetailParams
}>) {
  const { provider, id } = await params;

  const VALID_PROVIDERS = new Set(['aetc', 'jko', 'coursera', 'p2881']);

  if (!VALID_PROVIDERS.has(provider) || !isSaneUtf8(provider)) {
    return notFound();
  }

  if (!id || id.length > 250 || !isSaneUtf8(id)) {
    return notFound();
  }
  
  const res = await fetch(
    `${ENV.CCV_BASE_URL}/api/catalog/entry/?provider=${provider}&course_id=${id}`,
    { cache: 'no-store' }
  );
  if (!res.ok) return notFound();

  const course = await res.json();

  return (
    <>
      <Header />
      <CourseDetailClient
        initialCourse={course}
        initialProvider={provider}
      />
      <Footer />
    </>
  );
}