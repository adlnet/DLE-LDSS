'use client';

import {
  AcademicCapIcon,
  ArchiveIcon,
  UserIcon,
} from '@heroicons/react/outline';
import { ENV } from '@/lib/env';
import { useParams } from 'next/navigation';
import Dropdown, { DropdownOption } from '../../../../components/Dropdown';
import Footer from '../../../../components/Footer';
import Header from '../../../../components/Header';
import Image from 'next/image';
import React, { useEffect, useMemo, useState } from 'react';

interface Course {
  CourseTitle: string;
  CourseCode: string;
  CourseShortDescription: string;
  url: string;
  CourseProviderName: string;
  instructor: string;
  delivery: string;
  details: Array<{ title: string; content: string }>;
  date?: {
    start?: string;
    end?: string;
  };
}

interface CourseInstance {
  Thumbnail: string | undefined;
  StartDate: string;
  EndDate: string;
}

interface CombinedCourse extends Course {
  photo?: string;
  date?: {
    start?: string;
    end?: string;
  };
}

interface ApiResponse {
  hits: Array<{ Supplemental_Ledger: { Instance: number }; Course: Course; Course_Instance: CourseInstance }>;
}

interface MappedTerm {
  source: { alias: string; definition: string };
  target: { alias: string; definition: string };
  relationship: boolean;
}

export default function CourseDetailPage() {
  const params = useParams();
  const courseId = params?.courseId as string;
  const [data, setData] = useState<CombinedCourse | null>(null);
  const [labelMappings, setLabelMappings] = useState<MappedTerm[]>([]);
  const [loading, setLoading] = useState(true);

  // Providers and dropdown options
  const providerList = ['jko', 'coursera', 'aetc', 'p2881'];
  const providerOptions: DropdownOption[] = providerList.map((p) => ({
    id: p,
    name: p.charAt(0).toUpperCase() + p.slice(1),
  }));

  const [sourceProvider, setSourceProvider] = useState<string>('jko');
  const [targetProvider, setTargetProvider] = useState<string>('coursera');

  // Language toggle
  const [selectedLanguage, setSelectedLanguage] = useState<'source' | 'target'>('source');

  // Fetch mapping from remote API whenever target changes
  useEffect(() => {
      const controller = new AbortController();
      const fetchLabelMappings = async () => {
        try {
          const apiUrl = `${ENV.CCV_BASE_URL}/api/mapped-terms?source=${sourceProvider}&target=${targetProvider}`;
          const res = await fetch(apiUrl, { signal: controller.signal });
          if (!res.ok) throw new Error(`API fetch failed: ${res.status}`);
          const json: MappedTerm[] = await res.json();
          setLabelMappings(json);
        } catch (e) {
          if ((e as any).name === 'AbortError') return;
          console.error('Error fetching mapping:', e);
          setLabelMappings([]);
        }
      };
      fetchLabelMappings();
      return () => {
        controller.abort();
      };
    }, [targetProvider, sourceProvider]);

  // Build dictionary for label lookup
const labelMappingDict = useMemo(() => {
  const arr = Array.isArray(labelMappings) ? labelMappings : [];

  return arr.reduce<Record<string, string>>((acc, curr) => {
    if (curr?.source?.alias && curr?.target?.alias) {
      acc[curr.source.alias] = curr.target.alias;
    }
      return acc;
    }, {});
  }, [labelMappings]);

  const getLabel = (originalLabel: string): string => {
    if (selectedLanguage === 'target' && labelMappingDict[originalLabel]) {
      return labelMappingDict[originalLabel];
    }
    return originalLabel;
  };

  // Fetch course data from API on mount
  useEffect(() => {
      const controller = new AbortController();
      const fetchCourseData = async () => {
        try {
          const res = await fetch(`https://dev-xds-admin.deloitteopenlxp.com/es-api/?keyword=${courseId}`, { signal: controller.signal });
          if (!res.ok) {
            throw new Error('Failed to fetch course data');
          }
          const json: ApiResponse = await res.json();
          const hit = json.hits[0];
          if (hit) {
            const courseData = hit.Course;
            const courseInstanceData = hit.Course_Instance;
            const combinedData: CombinedCourse = {
              ...courseData,
              photo: courseInstanceData?.Thumbnail,
              date: {
                start: courseInstanceData?.StartDate,
                end: courseInstanceData?.EndDate,
              },
            };
            setData(combinedData);
          }
        } catch (error: any) {
          if (error.name === 'AbortError') return;
          console.error(error);
        } finally {
          setLoading(false);
        }
      };
      if (courseId) fetchCourseData();
      return () => {
        controller.abort();
      };
    }, [courseId]);

  // Set initial source provider based on fetched data
  useEffect(() => {
    if (data?.CourseProviderName) {
      setSourceProvider(data.CourseProviderName.toLowerCase());
    }
  }, [data]);

  if (loading) return <div>Loading...</div>;
  if (!data) return <div>Course data not available</div>;

  return (
    <>
      <Header />
      <div className="max-w-7xl mx-auto px-4 mt-4 flex gap-4">
        {/* Source Provider - disabled */}
        <Dropdown
          label="Source Provider"
          options={[{ id: sourceProvider, name: data.CourseProviderName }]}
          value={sourceProvider}
          disabled={true}
          onChange={() => {}}
        />
        {/* Target Provider */}
        <Dropdown
          label="Target Provider"
          options={providerOptions}
          value={targetProvider}
          onChange={(opt) => setTargetProvider(opt?.id ?? 'coursera')}
        />
        {/* Language Toggle */}
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium">Language:</span>
          <button
            onClick={() => setSelectedLanguage(selectedLanguage === 'source' ? 'target' : 'source')}
            className={`relative inline-flex items-center h-6 rounded-full w-11 transition-colors focus:outline-none ${
              selectedLanguage === 'target' ? 'bg-blue-600' : 'bg-gray-200'
            }`}
          >
            <span
              className={`inline-block w-5 h-5 transform bg-white rounded-full transition-transform ${
                selectedLanguage === 'target' ? 'translate-x-5' : 'translate-x-1'
              }`}
            />
          </button>
          <span className="text-sm">{selectedLanguage === 'source' ? 'Source' : 'Target'}</span>
        </div>
      </div>

      <div className="flex max-w-7xl px-4 mx-auto gap-8 mt-10">
        <div className="w-2/3">
          <h1 className="font-semibold text-4xl">{data.CourseTitle || 'Not Available'}</h1>
          <p className="my-2">
            <strong>{getLabel('Course Code')}: </strong>{data.CourseCode || 'Not Available'}
          </p>
          <p>{data.CourseShortDescription || 'Not Available'}</p>
        </div>
        {data.photo && (
          <Image
            src={data.photo}
            alt="Course"
            width={640}
            height={360}
            className="w-1/3 aspect-video object-contain"
          />
        )}
      </div>

      <div className="grid max-w-7xl px-4 mx-auto mt-10 grid-cols-2 gap-4">
        <span>
          <strong>{getLabel('StartDate')}: </strong>{data.date?.start || 'Not Available'}
        </span>
        <span>
          <strong>{getLabel('End Date')}: </strong>{data.date?.end || 'Not Available'}
        </span>
      </div>

      <div id="details-divider" className="bg-gray-200 mt-4">
        <div className="flex max-w-7xl mx-auto p-4 justify-between">
          <div className="flex items-center min-w-max gap-8">
            <div className="flex justify-center items-center gap-2">
              <ArchiveIcon className="h-10" />
              <span>
                <div className="text-sm font-semibold">{getLabel('Provider')}</div>
                <div className="text-sm">{data.CourseProviderName || 'Not Available'}</div>
              </span>
            </div>
            <div className="flex justify-center items-center gap-2">
              <UserIcon className="h-10" />
              <span>
                <div className="text-sm font-semibold">{getLabel('Instructor')}</div>
                <div className="text-sm">{data.instructor || 'Not Available'}</div>
              </span>
            </div>
            <div className="flex justify-center items-center gap-2">
              <AcademicCapIcon className="h-10" />
              <span>
                <div className="text-sm font-semibold">{getLabel('DeliveryMode')}</div>
                <div className="text-sm">{data.delivery || 'Not Available'}</div>
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="py-4 grid gap-5">
        {data.details?.map((detail, index) => (

          // Using `${title}-${index}` as React key:
          // - `details` is scoped to a single course, rendered via route `/courseDetail/[courseId]`
          // - Data is static per page load (no live edits/reordering)
          // - `title` alone may not be unique; combining with index ensures uniqueness within this context
          // - This avoids React's "don't use index as key" warning while remaining safe for this case
          // - If this page ever becomes dynamic, unique key will be needed, possible hash? -MB
          
          <div key={`${detail.title}-${index}`}className="grid grid-cols-5 w-full max-w-7xl px-4 mx-auto">
            <h2 className="min-w-max col-span-1 font-semibold">{getLabel(detail.title)}</h2>
            <p className="col-span-4">{detail.content || 'Not Available'}</p>
          </div>
        ))}
      </div>
      <Footer />
    </>
  );
}