'use client';

import Dropdown from './Dropdown';
import React, { useEffect, useState } from 'react';

interface TableRow {
  source?: {
    alias: string
    definition: string
  }
  target?: {
    alias: string
    definition: string
  }
  relationship?: boolean
}

interface Instance {
  url: string;
  name: string;
  displayName: string;
}

// MB - while I write tests lets number to keep track
const Table = () => {
  // 1. it gets its options for dropdowns from the API -good
  
  const [contexts, setContexts] = useState<Array<{ id: string; name: string }>>([]);

  // 2. it fetches mappings based on selected source/target - done
  const [pickedSource, setPickedSource] = useState<string>('');
  const [pickedTarget, setPickedTarget] = useState<string>('');

  //3. It builds table rows based on fetched mappings
  const [mappings, setMappings] = useState<TableRow[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // This is where it tries to fetch the contexts 
  // Where it uses set context, that is part of number 1.  - done
  // So 4. it fetches contexts from the API - done
  // If that fails, 5 a and b. throws an error it falls back to hardcoded values -done
  const fetchContexts = async () => {
    try {
      const res = await fetch('/api/instances');
      if (!res.ok) throw new Error(`Status ${res.status}`);
      const data: Record<string, Instance> = await res.json();
      if ('error' in data) throw new Error(data.error as unknown as string);

      const options = Object.values(data).map(inst => ({
        id: inst.name,
        name: inst.displayName,
      }));
      setContexts(options);
    } catch (err) {
      console.error('Error fetching contexts, falling back to dummy:', err);
      const fallback = ['coursera', 'jko', 'p2881', 'aetc'];
      setContexts(fallback.map(id => ({ id, name: id.charAt(0).toUpperCase() + id.slice(1) })));
    }
  };

  // 6. it fetches mappings from the remote API - done
  // If that fails, 7a and b. c it falls back to local .json files - done
  // If that fails, 8. it shows an error message - done 
  const fetchMappings = async (source: string, target: string, signal: AbortSignal) => {
    setLoading(true)
    setError(null)
  
    // Proxy through Nextjs route to avoid CORS issue
    const apiUrl = `/api/mapped-terms?source=${source}&target=${target}`;
  
    try {
      const res = await fetch(apiUrl)
      if (!res.ok) throw new Error(`Remote fetch failed: ${res.status}`)
      const data = await res.json()
      if (!Array.isArray(data)) throw new Error('Remote returned non-array')
      setMappings(data)
    } catch (remoteErr: any) {

      if (remoteErr.name === 'AbortError') {
        console.log('Fetch aborted');
        return;
      }

      console.warn('Remote fetch error, falling back to local file:', remoteErr)

      // .json fallback
      // 7d, e, f
      try {
        const fileName = `${source}-${target}.json`
        const res2 = await fetch(`/${fileName}`)
        if (!res2.ok) throw new Error(`Local file fetch failed: ${res2.status}`)
        const localData = await res2.json()
        if (!Array.isArray(localData)) throw new Error('Local file non-array')
        setMappings(localData)
      } catch (localErr: any) {
        if (localErr.name === 'AbortError') {
          console.log('Fetch aborted for local fallback.');
          return;
        }
        console.error('Local fallback failed:', localErr)
        setError(localErr.message || 'Unknown error loading mappings')
      }
    } finally {
      if (!signal.aborted) {
        setLoading(false)
      }
    }
  }

  // 9. loads contexts on initial render
  // Initial load of contexts
  useEffect(() => {
    fetchContexts();
  }, []);

  // 10. reloads mappings when source/target selection changes -  done
  // Reload mappings when selection changes
  useEffect(() => {
    if (pickedSource && pickedTarget && pickedSource !== pickedTarget) {
      const controller = new AbortController();
      const { signal } = controller;

      fetchMappings(pickedSource, pickedTarget, signal);

      return () => {
        controller.abort();
      };
    }
  }, [pickedSource, pickedTarget]);

// 11. renders and returns the table with dropdowns
// 11-a. renders dropdowns for source and target correctly or
// 11-b. shows an error message if mappings fail to load
  return (
    <div>
      {/* Dropdowns */}
      <div className="flex bg-gray-50 dark:bg-gray-700 p-4 shadow-sm">
        <Dropdown
          label="Source"
          options={contexts}
          onChange={opt => setPickedSource(opt?.id || '')}
        />
        <Dropdown
          label="Target"
          options={contexts}
          onChange={opt => setPickedTarget(opt?.id || '')}
        />
      </div>

      {/* Error message */}
      {error && (
        <div className="text-red-600 p-4">
          Error loading mappings: {error}. Showing fallback data.
        </div>
      )}

      {/* Loading / Table */}
      {loading ? (
        <div className="p-4">Loading mappings…</div>
      ) : (
        <div style={{ overflowX: 'auto', maxHeight: '80vh' }}>
          <table
            className="w-full text-sm text-left text-gray-500 dark:text-gray-400"
            style={{ tableLayout: 'fixed' }}
          >
            <thead className="sticky top-0 bg-gray-50 dark:bg-gray-700 font-medium">
              <tr>
              <th scope="col" className="px-6 py-3" style={{ width: '20%' }}>Source Alias</th>
              <th scope="col" className="px-6 py-3" style={{ width: '20%' }}>Source Definition</th>
              <th scope="col" className="px-6 py-3" style={{ width: '20%' }}>Relationship</th>
              <th scope="col" className="px-6 py-3" style={{ width: '20%' }}>Target Alias</th>
              <th scope="col" className="px-6 py-3" style={{ width: '20%' }}>Target Definition</th>
              </tr>
            </thead>
            <tbody>
              {mappings.length === 0 && (
                <tr>
                  <td colSpan={5} className="p-4 text-center">
                    No mappings to display.
                  </td>
                </tr>
              )}
              {mappings.map((row, idx) => (
                <tr key={idx} className="bg-white dark:bg-gray-800 border-b">
                  <td className="px-6 py-4">
                    {row.source?.alias ?? 'N/A'}
                  </td>
                  <td className="px-6 py-4">
                    {row.source?.definition ?? 'N/A'}
                  </td>
                  <td className="px-6 py-4">
                    {row.relationship
                      ? (
                        <span className="bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded-sm dark:bg-green-900 dark:text-green-300">
                          Equal
                        </span>
                      )
                      : (
                        <span className="bg-red-100 text-red-800 text-xs font-medium px-2.5 py-0.5 rounded-sm dark:bg-red-900 dark:text-red-300">
                          Missing
                        </span>
                      )}
                  </td>
                  <td className="px-6 py-4">
                    {row.target?.alias ?? 'N/A'}
                  </td>
                  <td className="px-6 py-4">
                    {row.target?.definition ?? 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Table;
