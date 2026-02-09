// const testtoken = require('./testToken.js')

// const username = "admin-user"
// const pretestJWT = testtoken.generatetestJWT(username, 'e2eadmin', 'admin@email.com')

// module.exports = {
//   e2e: {
//     baseUrl: 'https://ldss.staging.dso.mil/ldss-xss',
//     chromeWebSecurity: false,
//     setupNodeEvents(on, config) {
//       // Add the no-sandbox flags when launching Chrome
//       on('before:browser:launch', (browser = {}, launchOptions) => {
//         if (browser.name === 'chrome' || browser.name === 'chromium') {
//           launchOptions.args.push('--no-sandbox', '--disable-setuid-sandbox')
//         }
//         return launchOptions
//       })

//       return config
//     },
//   },
//   env: {
//     adminJWT: pretestJWT
//   },
//   defaultCommandTimeout: 9000,
//   video: true,
//   pageLoadTimeout: 60000
// }

const { defineConfig } = require('cypress')

const adminProperties = {
  "group-full": [
    "/Platform One/Products/adl-ousd/LDSS/IL2/roles/USER_SUPERUSER"
  ]
}

const testtoken = require("../util/tokenGeneration");
const dummyAdminJWT = testtoken.generateJWTFromEmail("admin@dummy.mil", adminProperties).jwt;

module.exports = defineConfig({

  e2e: {
    setupNodeEvents(on, config) {
      config.defaultCommandTimeout = 10000;
      config.baseUrl = config.baseUrl + '/ldss-xss';

      config.hideXHRInCommandLog = true;

      return config
    },
    env: {
      jwt: dummyAdminJWT, 
    }
  },
});
