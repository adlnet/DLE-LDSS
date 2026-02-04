'use client'

import Dropdown, { DropdownOption } from '../../../../..//components/Dropdown'
import React, { useState } from 'react'

const providerOptions: DropdownOption[] = [
  { id: 'aetc', name: 'AETC' },
  { id: 'jko', name: 'JKO' },
]

export default function CourseControls({
  initialProvider,
}: Readonly<{
  initialProvider: 'aetc' | 'jko'
}>) {
  const [sourceProvider] = useState(initialProvider)
  const [targetProvider, setTargetProvider] = useState<string>('coursera')
  const [language, setLanguage] = useState<'source' | 'target'>('source')

  return (
    <div className="max-w-7xl mx-auto px-4 mt-4 flex gap-4">
      <Dropdown
        label="Source Provider"
        options={providerOptions}
        value={sourceProvider}
        disabled
        onChange={() => {}}
      />
      <Dropdown
        label="Target Provider"
        options={providerOptions}
        value={targetProvider}
        onChange={(opt) => setTargetProvider(opt?.id ?? 'coursera')}
      />
      <div className="flex items-center space-x-2">
        <span className="text-sm font-medium">Language:</span>
        <button
          onClick={() => setLanguage(language === 'source' ? 'target' : 'source')}
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
        <span className="text-sm">{language === 'source' ? 'Source' : 'Target'}</span>
      </div>
    </div>
  )
}