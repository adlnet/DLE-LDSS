// ***********************************************************
// This example support/e2e.ts is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

if (!process.stdout) {
  process.stdout = {
    isTTY: true,
    write: function(_chunk, _encoding, _callback) { return true; }
  };
}

if (!process.stderr) {
  process.stderr = {
    isTTY: true,
    write: function(_chunk, _encoding, _callback) { return true; }
  };
}

// Import commands.js using ES2015 syntax:
require('./commands');

Cypress.on('uncaught:exception', function(err, runnable) {
  console.log('uncaught:exception', err);
  return false;
});

require('dotenv').config({ path: '.env.local' });
var testtoken = require('./testToken.js');

// Generate DEV_JWT dynamically at runtime
if (process.env.NODE_ENV === 'development' && !process.env.DEV_JWT) {
  process.env.DEV_JWT = testtoken.generateLocalJWT(
    'admin-user',
    'e2eadmin',
    'admin@email.com',
    process.env.JWT_SECRET || 'dummy_local_secret'
  );
}
