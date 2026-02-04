import { hasNullByte, isSaneUtf8 } from './utils';

describe('utils', () => {
  describe('isSaneUtf8', () => {
    it('returns true for normal ASCII text', () => {
      expect(isSaneUtf8('Hello World')).toBe(true);
    });

    it('returns false for text with disallowed bad chars (non-breaking space)', () => {
      expect(isSaneUtf8('Hello\u00A0World')).toBe(false);
    });

    it('returns false for text with disallowed Unicode thin space', () => {
      expect(isSaneUtf8('Test\u2009Here')).toBe(false);
    });

    it('returns false if regex fails (invalid sequence)', () => {
      // Inject something outside the regex range
      const invalid = String.fromCharCode(0xDC00); // low surrogate by itself
      expect(isSaneUtf8(invalid)).toBe(false);
    });
  });

  describe('hasNullByte', () => {
    it('returns true when string contains \\0', () => {
      expect(hasNullByte('abc\0def')).toBe(true);
    });

    it('returns false when string does not contain \\0', () => {
      expect(hasNullByte('abcdef')).toBe(false);
    });
  });
});
