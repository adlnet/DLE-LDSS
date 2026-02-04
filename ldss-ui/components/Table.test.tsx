import { render, screen, waitFor, within } from '@testing-library/react';
import { stat } from 'fs';
import Dropdown from './Dropdown';
import React from 'react';
import Table from '../components/Table'; 
import userEvent from '@testing-library/user-event';


describe('Table Component', () => {
  beforeEach(() => {
    const makeResponse = (body: any, status = 200) =>
      new Response(JSON.stringify(body), {
        status,
        headers: { 'Content-Type': 'application/json' },
      });

    global.fetch = jest.fn(async (input: RequestInfo | URL) => {
      const url = String(input);

      if (url.endsWith('/api/contexts')) {
        return makeResponse({
          coursera: { url: '...', name: 'coursera', displayName: 'Coursera' },
          jko: { url: '...', name: 'jko', displayName: 'JKO' },
        });
      }

      if (url.endsWith('/api/instances')) {
        return makeResponse({
          inst1: { url: 'x', name: 'aetc', displayName: 'AETC' },
          inst2: { url: 'y', name: 'jko', displayName: 'JKO' },
        });
      }

      if (url.includes('/api/mapped-terms')) {
        return makeResponse([
          { source: { alias: 'Provider' }, target: { alias: 'Proveedor' } },
        ]);
      }

      if (url.endsWith('/api/mappings')) {
        return makeResponse([]); // empty list is fine
      }

      throw new Error(`Unexpected fetch call: ${url}`);
    }) as jest.Mock;
  });

  afterEach(() => {
    jest.clearAllMocks();
    jest.restoreAllMocks();
  });

  it('fetches contexts and passes them to the Dropdowns, rendering them correctly', async () => {
    // Arrange: mock fetch with sample data
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          coursera: { url: '...', name: 'coursera', displayName: 'Coursera' },
          jko: { url: '...', name: 'jko', displayName: 'JKO' },
        }),
      })
    ) as jest.Mock;
  
    render(<Table />);
  
    // Wait for options to load (use findByLabelText to wait on async).
    const sourceSelect = await screen.findByLabelText('Source');
    const targetSelect = await screen.findByLabelText('Target');

    // Open dropdown by clicking (or just inspect the DOM options).
    expect(sourceSelect).toHaveDisplayValue('Select Source');
    expect(targetSelect).toHaveDisplayValue('Select Target');
    
    // The options should now include Coursera and JKO.
    expect(within(sourceSelect).getByRole('option', { name: 'Coursera' })).toBeInTheDocument();
    expect(within(targetSelect).getByRole('option', { name: 'Coursera' })).toBeInTheDocument();
    expect(within(sourceSelect).getByRole('option', { name: 'JKO' })).toBeInTheDocument();
    expect(within(targetSelect).getByRole('option', { name: 'JKO' })).toBeInTheDocument();
      
    // If selected the value needs to change.
    await userEvent.selectOptions(sourceSelect, 'coursera');
    expect(sourceSelect).toHaveValue('coursera');
    
    await userEvent.selectOptions(targetSelect, 'jko');
    expect(targetSelect).toHaveValue('jko');
  });

  it('uses fallback contexts when API fetch fails', async () => {
    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('API failure'));
  
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
  
    render(<Table />);
  
    const sourceDropdown = await screen.findByLabelText('Source');
  
    // Fallback options should be there, they are captilized by code.
    expect(within(sourceDropdown).getByRole('option', { name: 'Coursera' })).toBeInTheDocument();
    expect(within(sourceDropdown).getByRole('option', { name: 'Jko' })).toBeInTheDocument();
    expect(within(sourceDropdown).getByRole('option', { name: 'P2881' })).toBeInTheDocument();
    expect(within(sourceDropdown).getByRole('option', { name: 'Aetc' })).toBeInTheDocument();
  
    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('Error fetching contexts, falling back to dummy:'),
      expect.any(Error)
    );
  
    consoleSpy.mockRestore();
  });

  it('falls back when API fetch returns !ok response', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: () => Promise.resolve({}), // Shouldn’t even get here.
    });
  
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
  
    render(<Table />);
  
    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Error fetching contexts, falling back to dummy:'),
        expect.any(Error)
      );
    });
  });

  it('falls back when API response contains error key', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ error: 'Something went wrong, error.' }),
    });
  
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
  
    render(<Table />);
  
    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Error fetching contexts, falling back to dummy:'),
        expect.any(Error)
      );
    });
  });


    it('fetches mappings when valid source and target are selected', async () => {
        // Arrange mocks for contexts first
        global.fetch = jest.fn()

          // First fetch: contexts
          .mockResolvedValueOnce({
            ok: true,
            json: () => Promise.resolve({
              coursera: { url: '...', name: 'coursera', displayName: 'Coursera' },
              jko: { url: '...', name: 'jko', displayName: 'JKO' },
            }),
          })

          // Second fetch: mappings
          .mockResolvedValueOnce({
            ok: true,
            json: () => Promise.resolve([
              { source: { alias: 'test1', definition: 'def1' }, target: { alias: 'test2', definition: 'def2' }, relationship: true }
            ]),
          });
      
        render(<Table />);
      
        const source = 'coursera';
        const target = 'jko';

        // Act — Select source & target (must be different).
        const sourceSelect = await screen.findByLabelText('Source');
        const targetSelect = await screen.findByLabelText('Target');
      
        await userEvent.selectOptions(sourceSelect, source);
        await userEvent.selectOptions(targetSelect, target);;
      
        // Assert — Wait for table row to appear.
        await waitFor(() => {
          expect(screen.getByText('test1')).toBeInTheDocument();
          expect(screen.getByText('test2')).toBeInTheDocument();
        });
      
        // Mimic the proxy:
        const apiUrl = `/api/mapped-terms?source=${source}&target=${target}`;
  
        // Assert fetch called twice (contexts + mappings).
        expect(global.fetch).toHaveBeenCalledTimes(2);
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining(apiUrl)
        );
      });
     
    it('throw an error showing response status if response is not ok in fetchMappings', async () => {
      // Arrange mocks for contexts first.
      // First call is done by fetchContexts.
      // Second call is done by fetchMappings.
      global.fetch = jest.fn()

        // First fetch: contexts
        .mockResolvedValueOnce({
          ok: true,
          status: 200,

        })

      // Second fetch fails (local fallback)
      .mockResolvedValueOnce({
        ok: false,
        status: 404,
      });

    // Spy on log. 
    const consoleSpy = jest.spyOn(console, 'warn');

    // trigger fetch mappings:       
        render(<Table />);
      
    // Pick the dropdowns
    const sourceSelect = await screen.findByLabelText('Source');
    const targetSelect = await screen.findByLabelText('Target');
  
    // Select options to trigger fetchMappings
    await userEvent.selectOptions(sourceSelect, 'coursera');
    await userEvent.selectOptions(targetSelect, 'jko');

    // Wait for the error to be logged

    const errorshouldbe = 'Remote fetch failed: 404';
    await waitFor(() => {
      expect(consoleSpy).toHaveBeenNthCalledWith(
        1,
        "Remote fetch error, falling back to local file:",
        expect.objectContaining({
          message: expect.stringContaining(errorshouldbe),
        })
      );
    });
  });

      it('throw an error showing response status if response from URL is not a json', async () => {
        // Arrange mocks for contexts first
        // first call is done by fetchContexts
        // second call is done by fetchMappings
        global.fetch = jest.fn()

          // First fetch: contexts
          .mockResolvedValueOnce({
            ok: false,
            status: 500,

          })

    // Second fetch fails (local fallback)
    .mockResolvedValueOnce({
       
    ok: true,
    status: 200,
    json: () => Promise.resolve("not-an-array")  // Simulate a non-array response

    });

  // Spy on log. 
  const consoleSpy = jest.spyOn(console, 'warn');

  // trigger fetch mappings:       
        render(<Table />);
      
        // Pick the dropdowns
        const sourceSelect = await screen.findByLabelText('Source');
        const targetSelect = await screen.findByLabelText('Target');
      
        // Select options to trigger fetchMappings
        await userEvent.selectOptions(sourceSelect, 'coursera');
        await userEvent.selectOptions(targetSelect, 'jko');

        // Wait for the error to be logged

    // Assert error, which is part passed in in the code and part the error the response provides.
  
    const errorshouldbe = 'Remote returned non-array';
    await waitFor(() => {
      expect(consoleSpy).toHaveBeenNthCalledWith(
        1,
        "Remote fetch error, falling back to local file:",
        expect.objectContaining({
          message: expect.stringContaining(errorshouldbe),
        })
      );
    });
});

  it('fetches mappings from fallback JSON when remote fetch fails', async () => {
    (global.fetch as jest.Mock).mockImplementation((url: string) => {
      if (url.startsWith('https://ccv.ldss.tla.adlnet.gov/api/mapped-terms')) {
        return Promise.reject(new Error('Remote fetch failed'));  // Simulate remote failure
      }
      if (url === '/coursera-jko.json') {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([
            { source: { alias: 'localSource' }, target: { alias: 'localTarget' }, relationship: true }
          ]),
        });  // Simulate successful local JSON fetch
      }
      return Promise.reject(new Error('Unknown URL in fetch mock'));
    });

    render(<Table />);

    // Pick the dropdowns
    const sourceSelect = await screen.findByLabelText('Source');
    const targetSelect = await screen.findByLabelText('Target');

    // Select options to trigger fetchMappings
    await userEvent.selectOptions(sourceSelect, 'coursera');
    await userEvent.selectOptions(targetSelect, 'jko');

    // Assert fallback data rendered
    expect(await screen.findByText('localSource')).toBeInTheDocument();
    expect(screen.getByText('localTarget')).toBeInTheDocument();
  });

  it('throws a "local file fetch failed" error if local json is not found', async () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
  
    // Arrange fetch mock for all 3 calls.
    (global.fetch as jest.Mock).mockImplementation((url: string) => {
      // 1st call: Remote fetch
      if (url.startsWith('https://ccv.ldss.tla.adlnet.gov/api/mapped-terms')) {
        return Promise.resolve({ ok: false, status: 500 }); // simulate remote failure
      }

      // 2nd call: Local file fetch
      if (url === '/coursera-jko.json') {
        return Promise.resolve({ ok: false, status: 404 }); // simulate local file missing
      }

      // Default
      return Promise.reject(new Error('Unexpected fetch call: ' + url));
    });
  
    render(<Table />);
  
    // Select source and target to trigger fetchMappings.
    const sourceSelect = await screen.findByLabelText('Source');
    const targetSelect = await screen.findByLabelText('Target');
  
    await userEvent.selectOptions(sourceSelect, 'coursera');
    await userEvent.selectOptions(targetSelect, 'jko');
  
    const errorshouldbe = 'Local file fetch failed: 404';
    await waitFor(() => {
      expect(consoleSpy).toHaveBeenNthCalledWith(
        2,
        "Local fallback failed:",
        expect.objectContaining({
          message: expect.stringContaining(errorshouldbe),
        })
      );
    });

  });
  it('displays error message to console log if specific abort error received when trying to contact API)', async () => {
    //Mock source and target.
    const source = 'coursera';
    const target = 'jko';

    //Mock apiUrl
    const apiUrl = `/api/mapped-terms?source=${source}&target=${target}`;
  
    // Arrange fetch mock for all 3 calls.
      (global.fetch as jest.Mock).mockImplementation((url: string) => {
        // 1st call: Remote fetch.
        if (url === apiUrl) {
          return Promise.resolve({
            ok: true,
            status: 200,
            json: () => {
              const err = new Error("This request was aborted");
              err.name = 'AbortError';
              throw err;
            }
        
          });
        }

        // Default
        return Promise.reject(new Error('Unexpected fetch call: ' + url));
      });


      // Spy on 'error', this is the block that tries to fetch local json.
      const consoleSpyL = jest.spyOn(console, 'log');
    render(<Table />);

    // Pick the dropdowns
    const sourceSelect = await screen.findByLabelText('Source');
    const targetSelect = await screen.findByLabelText('Target');

    // Select options to trigger fetchMappings
    await userEvent.selectOptions(sourceSelect, 'coursera');
    await userEvent.selectOptions(targetSelect, 'jko');

    const testErrorW = 'Remote fetch failed: ';

    // When it is called by contexts and fails.
    expect(consoleSpyL).toHaveBeenNthCalledWith(1,
      'Fetch aborted'     
    );


  });   
  it('displays error message when both remote and local fetch fail', async () => {
    //Mock source and target.
    const source = 'coursera';
    const target = 'jko';

    //Mock apiUrl
    const apiUrl = `/api/mapped-terms?source=${source}&target=${target}`;
  
    // Arrange fetch mock for all 3 calls.
      (global.fetch as jest.Mock).mockImplementation((url: string) => {
        // 1st call: Remote fetch.
        if (url.startsWith(apiUrl)) {
          return Promise.resolve({ ok: false, status: 500 }); // simulate remote failure
        }
    
        // 2nd call: Local file fetch.
        if (url === '/coursera-jko.json') {
          return Promise.resolve({
            ok: true,
            status: 200,
            json: () => { throw new Error ("Unknown Error"); }
        
          });
        }

        // Default
        return Promise.reject(new Error('Unexpected fetch call: ' + url));
      });

      // Spy on 'warn', this is the block that tries to fetch html.
      const consoleSpyW = jest.spyOn(console, 'warn');

      // Spy on 'error', this is the block that tries to fetch local json.
      const consoleSpyE = jest.spyOn(console, 'error');
    render(<Table />);

    // Pick the dropdowns
    const sourceSelect = await screen.findByLabelText('Source');
    const targetSelect = await screen.findByLabelText('Target');

    // Select options to trigger fetchMappings
    await userEvent.selectOptions(sourceSelect, 'coursera');
    await userEvent.selectOptions(targetSelect, 'jko');

    const testErrorW = 'Remote fetch failed: ';

    expect(consoleSpyW).toHaveBeenCalledWith(
      'Remote fetch error, falling back to local file:',
      expect.objectContaining({
        message: expect.stringContaining(testErrorW),
      })
    );

    // When it is called by contexts and fails.
    expect(consoleSpyE).toHaveBeenNthCalledWith(1,
      'Error fetching contexts, falling back to dummy:',
      expect.any(Error)      
    );

    // when it is called in fetchMAppings and fails
    expect(consoleSpyE).toHaveBeenNthCalledWith(2,
      'Local fallback failed:',
      expect.any(Error)      
    );
    
    expect(consoleSpyE).toHaveBeenCalledTimes(2);
    expect(screen.getByText(/Showing fallback data/i)).toBeInTheDocument();
    expect(screen.getByText(/Unknown error/i)).toBeInTheDocument();

  });   

  it('displays error message to console log if local json cannot be retrieved', async () => {
    //Mock source and target.
    const source = 'coursera';
    const target = 'jko';

    //Mock apiUrl
    const apiUrl = `/api/mapped-terms?source=${source}&target=${target}`;
  
    // Arrange fetch mock for all 3 calls.
      (global.fetch as jest.Mock).mockImplementation((url: string) => {
        // 1st call: Remote fetch.
        if (url.startsWith(apiUrl)) {
          return Promise.resolve({ ok: false, status: 500 }); // simulate remote failure
        }
    
        // 2nd call: Local file fetch.
        if (url === '/coursera-jko.json') {
          return Promise.resolve({
            ok: true,
            status: 200,
            json: () => {
              const err = new Error("This request was aborted");
              err.name = 'AbortError';
              throw err;
            }
        
          });
        }

        // Default
        return Promise.reject(new Error('Unexpected fetch call: ' + url));
      });


      // Spy on 'error', this is the block that tries to fetch local json.
      const consoleSpyL = jest.spyOn(console, 'log');
    render(<Table />);

    // Pick the dropdowns
    const sourceSelect = await screen.findByLabelText('Source');
    const targetSelect = await screen.findByLabelText('Target');

    // Select options to trigger fetchMappings
    await userEvent.selectOptions(sourceSelect, 'coursera');
    await userEvent.selectOptions(targetSelect, 'jko');

    const testErrorW = 'Remote fetch failed: ';

    // When it is called by contexts and fails.
    expect(consoleSpyL).toHaveBeenNthCalledWith(1,
      'Fetch aborted for local fallback.'     
    );


  });   

  it('renders the table with dropdowns and handles selection changes', async () => {

    // Arrange: mock fetch with sample data.
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          coursera: { id: 'coursera', name: 'coursera', displayName: 'Coursera' },
          jko: { id: 'jko', name: 'jko', displayName: 'JKO' },
        }),
      })
    ) as jest.Mock;
  
    render(<Table />);
  
    const sourceDropdown = await screen.findByLabelText(/Source/i);
    const targetDropdown = await screen.findByLabelText(/Target/i);
    
    expect(sourceDropdown).toBeInTheDocument();
    expect(targetDropdown).toBeInTheDocument();

    // If selected the value needs to change.
    await userEvent.selectOptions(sourceDropdown, 'coursera');
    expect(sourceDropdown).toHaveValue('coursera');
    
    await userEvent.selectOptions(targetDropdown, 'jko');
    expect(targetDropdown).toHaveValue('jko');

    // Now change the entry.
    await userEvent.selectOptions(sourceDropdown, '');
    expect(sourceDropdown).toHaveValue('');
    
    await userEvent.selectOptions(targetDropdown, '');
    expect(targetDropdown).toHaveValue('');

  });  
  
  it('renders N/A when source or alias is missing', async () => {
      // Step 1: Mock fetch for both contexts and mappings.
      global.fetch = jest.fn()

        // First call: contexts.
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            coursera: { name: 'coursera', url: '', displayName: 'Coursera' },
            jko: { name: 'jko', url: '', displayName: 'JKO' }
          })
        })

        // Second call: mappings.
        .mockResolvedValueOnce({
          ok: true,
          json: async () => [
            {
              // No alias — triggers 'N/A'.
              source: { definition: 'Something' },
              target: { alias: 'T1', definition: 'TD1' },
              relationship: true
            },
            {
              // No source — triggers 'N/A'.
              target: { alias: 'T2', definition: 'TD2' },
              relationship: false
            }
          ]
        });
  
      // Step 2: Render the table.
      render(<Table />);
  
      // Step 3: Wait for dropdowns to load and pick source/target.
      const sourceSelect = await screen.findByLabelText('Source');
      const targetSelect = await screen.findByLabelText('Target');
  
      await userEvent.selectOptions(sourceSelect, 'coursera');
      await userEvent.selectOptions(targetSelect, 'jko');
  
      // Step 4: Wait for table rows to appear.
      await waitFor(() => {
        expect(screen.getAllByText('N/A').length).toBeGreaterThan(0);
      });
  
      // Step 5: Assert specific fallback cells.
      expect(screen.getAllByText('N/A')).toHaveLength(3); // Both rows.
      expect(screen.getByText('T1')).toBeInTheDocument();
      expect(screen.getByText('T2')).toBeInTheDocument();
    });

    it('renders N/A when target alias or definition is missing', async () => {
      global.fetch = jest.fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            coursera: { name: 'coursera', url: '', displayName: 'Coursera' },
            jko: { name: 'jko', url: '', displayName: 'JKO' }
          })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => [
            {
              source: { alias: 'S1', definition: 'SD1' },
              target: { definition: 'TD1' }, // No alias.
              relationship: true
            },
            {
              source: { alias: 'S2', definition: 'SD2' },
              target: { alias: 'T2' }, // No definition.
              relationship: true
            },
            {
              source: { alias: 'S3', definition: 'SD3' },
              target: undefined, // Fully missing.
              relationship: true
            }
          ]
        });
    
      render(<Table />);
    
      const sourceSelect = await screen.findByLabelText('Source');
      const targetSelect = await screen.findByLabelText('Target');
    
      await userEvent.selectOptions(sourceSelect, 'coursera');
      await userEvent.selectOptions(targetSelect, 'jko');
    
      await waitFor(() => {
        // There should be 3 N/A cells for alias (missing, undefined, undefined).
        expect(screen.getAllByText('N/A').length).toBeGreaterThanOrEqual(3);
      });
    
      // Alias fallback checks.
      const naCells = screen.getAllByText('N/A');
      expect(naCells).toEqual(
        expect.arrayContaining([
          expect.any(HTMLElement) // Alias missing.
        ])
      );
    
      // Check we still get valid values for source cells
      expect(screen.getByText('S1')).toBeInTheDocument();
      expect(screen.getByText('S2')).toBeInTheDocument();
      expect(screen.getByText('S3')).toBeInTheDocument();
    });
    
});
