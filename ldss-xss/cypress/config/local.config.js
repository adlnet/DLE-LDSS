const { defineConfig } = require('cypress');

const testtoken = require('../util/tokenGeneration.js');

const testID1 = testtoken.generateTestID();
const testID2 = testtoken.generateTestID();

module.exports = defineConfig({
  e2e: {
    specPattern: [
      "cypress/e2e/*.cy.{js,jsx,ts,tsx}", 
      // "cypress/e2e/uitesting/framework.cy.{js,jsx,ts,tsx}", 
      //'cypress/e2e/sdelement/t85.cy.{js,jsx,ts,tsx}'
    ],
    baseUrl: 'http://localhost',
    experimentalStudio: true,
    hideXHRInCommandLog: true
  },
  env: {
    testJWT1: testID1.jwt,
    testJWT2: testID2.jwt,
  },
  defaultCommandTimeout: 9000,

});

