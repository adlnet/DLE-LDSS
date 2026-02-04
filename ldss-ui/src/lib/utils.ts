const BAD_CHARS = new Set<string>([
    '\u00A0',
    '\u202F',
    '\u2000', '\u2001', '\u2002', '\u2003', '\u2004', '\u2005', '\u2006',
    '\u2007', '\u2008', '\u2009', '\u200A',
    '\u205F',
    '\u3000',
]);

const ALLOWABLE_UTF8_REGEX = new RegExp(
    /^([\u0020-\u007E]|[\u00C2-\u00DF][\u0080-\u00BF]|[\u00E0-\u00EF][\u0080-\u00BF]{2}|[\u00F0-\u00F4][\u0080-\u00BF]{3})*$/,
    'u'
);

function hasBadChars(s: string): boolean {
    for (const char of s) {
        if (BAD_CHARS.has(char)) {
            return true;
        }
    }
    return false;
}

export function isSaneUtf8(s: string): boolean {
    if (hasBadChars(s)) {
        return false;
    }
    return ALLOWABLE_UTF8_REGEX.test(s);
}

export function hasNullByte(s: string): boolean {
    return s.includes('\0');
}
