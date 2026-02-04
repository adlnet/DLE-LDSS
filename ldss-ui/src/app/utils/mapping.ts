import { ENV } from '@/lib/env';
export interface Term {
    alias: string;
    definition: string;
  }
  
  export interface MappedTerm {
    source: Term;
    target?: Term;
    relationship?: boolean;
  }
  
  /**
   * Fetch term mappings from the url.
   * @param sourceProvider - The source alias
   * @param targetProvider - The target alias
   * @returns Promise resolving to an array of mapped terms.
   */

  export async function fetchMappedTerms(
    sourceProvider: string,
    targetProvider: string
  ): Promise<MappedTerm[]> {
    const url = `${ENV.CCV_BASE_URL}/api/mapped-terms?source=${encodeURIComponent(
      sourceProvider
    )}&target=${encodeURIComponent(targetProvider)}`;
  
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to fetch mapped terms: ${response.status} ${response.statusText}`);
    }
  
    const data = (await response.json()) as MappedTerm[];
    return data;
  }
  
  /**
   * Finds the corresponding alias for a given alias in the mappings
   * If the alias matches a source term, returns the target alias, and vice versa
   * @param sourceAlias - The source system alias.
   * @param targetAlias - The target system alias.
   * @param alias - The alias to look up.
   * @returns Promise resolving to the matching alias, or null if not found.
   */

  export async function findMatchingAlias(
    sourceAlias: string,
    targetAlias: string,
    alias: string
  ): Promise<string | null> {
    const mappings = await fetchMappedTerms(sourceAlias, targetAlias);
  
    for (const mapping of mappings) {
      // If the alias matches the source and there is a target, return the target alias
      if (mapping.source.alias === alias && mapping.target) {
        return mapping.target.alias;
      }

      // If the alias matches the target and there is a source, return the source alias
      if (mapping.target?.alias === alias) {
        return mapping.source.alias;
      }
    }
  
    return null;
  }
  