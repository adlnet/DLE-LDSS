'use client';

import { AcademicCapIcon, ArchiveIcon, UserIcon } from '@heroicons/react/outline';
import { MappedTerm } from '../../../utils/mapping';
import Dropdown, { DropdownOption } from '../../../../..//components/Dropdown';
import Image from 'next/image';
import React, { useEffect, useState } from 'react';

interface CourseData {
  [key: string]: any;
}

export default function CourseDetailClient({
  initialCourse,
  initialProvider,
}: Readonly<{
  initialCourse: CourseData;
  initialProvider: string;
}>) {
  const [sourceProvider] = useState<string>(initialProvider);
  const [targetProvider, setTargetProvider] = useState<string>(
    initialProvider === 'aetc' ? 'jko' : 'aetc'
  );
  const [language, setLanguage] = useState<'source' | 'target'>('source');
  const [labelMap, setLabelMap] = useState<Record<string, string>>({});
  const [instanceOptions, setInstanceOptions] = useState<DropdownOption[]>([]);

  useEffect(() => {
    const abortController = new AbortController();
    async function loadInstances() {
      try {
        const res = await fetch('/api/instances', { signal: abortController.signal });
        if (!res.ok) throw new Error(`Status ${res.status}`);
        const json: Record<
          string,
          { url: string; name: string; displayName: string }
        > = await res.json();

        const opts: DropdownOption[] = Object.values(json).map((inst) => ({
          id: inst.name,
          name: inst.displayName,
        }));
        setInstanceOptions(opts);
      } catch (err: any) {
        if (err.name === 'AbortError') return;
        console.error('Error loading instances:', err);
        setInstanceOptions([]);
      }
    }
    loadInstances();
    return () => {
      abortController.abort();
    };
  }, []);

  // fetch your mappings whenever source/target change
  useEffect(() => {
    const abortController = new AbortController();
    async function loadMappings() {
      try {
        const res = await fetch(
          `/api/mapped-terms?source=${sourceProvider}&target=${targetProvider}`,
          { signal: abortController.signal }
        );
        if (!res.ok) throw new Error(`Status ${res.status}`);

        const data = await res.json();

        if (!Array.isArray(data)) {
          console.error('Expected array of mappings, got:', data);
          setLabelMap({});
          return;
        }

        const map: Record<string, string> = {};
        data.forEach((m: MappedTerm) => {
          if (m.source?.alias && m.target?.alias) {
            map[m.source.alias] = m.target.alias;
            map[m.target.alias] = m.source.alias;
          }
        });
        setLabelMap(map);
      } catch (err: any) {
        if (err.name === 'AbortError') return;
        console.error('Error loading mappings:', err);
        setLabelMap({});
      }
    }
    if (instanceOptions.length) {
      loadMappings();
    }
    return () => {
      abortController.abort();
    };
  }, [sourceProvider, targetProvider, instanceOptions]);

  const getLabel = (alias: string) =>
    language === 'source' ? alias : labelMap[alias] ?? alias;

  const course = initialCourse;

  return (
    <div className="max-w-7xl mx-auto px-4 mt-4">
      <div className="flex gap-4">
        <Dropdown
          label="Source Provider"
          options={instanceOptions}
          value={sourceProvider}
          disabled
          onChange={() => {}}
        />
        <Dropdown
          label="Target Provider"
          options={instanceOptions}
          value={targetProvider}
          onChange={(opt) => opt && setTargetProvider(opt.id)}
        />
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium">Language:</span>
          <button
            onClick={() =>
              setLanguage((lang) => (lang === 'source' ? 'target' : 'source'))
            }
            className={`relative inline-flex items-center h-6 rounded-full w-11 transition-colors focus:outline-none ${
              language === 'target' ? 'bg-blue-600' : 'bg-gray-200'
            }`}
          >
            <span
              className={`inline-block w-5 h-5 transform bg-white rounded-full transition-transform ${
                language === 'target' ? 'translate-x-5' : 'translate-x-1'
              }`}
            />
          </button>
          <span className="text-sm">
            {language === 'source' ? 'Source' : 'Target'}
          </span>
        </div>
      </div>

      <div className="flex max-w-7xl px-4 mx-auto gap-8 mt-10">
        <div className="w-2/3">
          <h1 className="font-semibold text-4xl">
            {course.course_name || course.learning_resource_name}
          </h1>

          {'course_name' in course ? (
            <p className="my-2">
              <strong>{getLabel('Agency')}:</strong>{' '}
              {course.agency_organization}
            </p>
          ) : (
            <p className="my-2">
              <strong>{getLabel('Identifier')}:</strong>{' '}
              {course.learning_resource_identifier}
            </p>
          )}

          <p>{course.course_description || course.learning_resource_description}</p>
        </div>

        {course.learning_resource_name && (
          <Image
            src="/placeholder-course.png"
            alt="Course"
            width={640}
            height={360}
            className="w-1/3 aspect-video object-contain"
          />
        )}
      </div>

      <div className="grid max-w-7xl px-4 mx-auto mt-10 grid-cols-2 gap-4">
        {course.course_name ? (
          <>
            <span>
              <strong>{getLabel('Format')}:</strong> {course.course_material_format}
            </span>
            <span>
              <strong>{getLabel('Location')}:</strong>{' '}
              {course.course_administered_location}
            </span>
          </>
        ) : (
          <>
            <span>
              <strong>{getLabel('Duration')}:</strong> {course.duration} hrs
            </span>
            <span>
              <strong>{getLabel('Mode')}:</strong> {course.delivery_mode}
            </span>
          </>
        )}
      </div>

      <div id="details-divider" className="bg-gray-200 mt-4">
        <div className="flex max-w-7xl mx-auto p-4 justify-between">
          <div className="flex items-center min-w-max gap-8">
            <div className="flex justify-center items-center gap-2">
              <ArchiveIcon className="h-10" />
              <span>
                <div className="text-sm font-semibold">{getLabel('Provider')}</div>
                <div className="text-sm">{sourceProvider.toUpperCase()}</div>
              </span>
            </div>
            <div className="flex justify-center items-center gap-2">
              <UserIcon className="h-10" />
              <span>
                <div className="text-sm font-semibold">{getLabel('Instance')}</div>
                <div className="text-sm">{course.instance || 'N/A'}</div>
              </span>
            </div>
            <div className="flex justify-center items-center gap-2">
              <AcademicCapIcon className="h-10" />
              <span>
                <div className="text-sm font-semibold">{getLabel('Delivery_Method')}</div>
                <div className="text-sm">{course.delivery_mode}</div>
              </span>
            </div>
          </div>
        </div>
      </div>

      {course.comments && (
        <div className="py-4 grid gap-5">
          <div className="grid grid-cols-5 w-full max-w-7xl px-4 mx-auto">
            <h2 className="min-w-max col-span-1 font-semibold">
              {getLabel('Comments')}
            </h2>
            <p className="col-span-4">{course.comments}</p>
          </div>
        </div>
      )}
    </div>
  );
}