const crypto = require('crypto');
const origCreateHash = crypto.createHash;

crypto.createHash = (algorithm, options) => {
  // Swap SHA-1 to MD5
  if (algorithm === 'sha1' || algorithm === 'md5') {
    algorithm = 'sha256';
  }
  return origCreateHash(algorithm, options);
};