module.exports = {
  e2e: {
    baseUrl: 'https://ldss.staging.dso.mil',
    chromeWebSecurity: false,
    setupNodeEvents(on, config) {
      // Add the no-sandbox flags when launching Chrome
      on('before:browser:launch', (browser = {}, launchOptions) => {
        if (browser.name === 'chrome' || browser.name === 'chromium') {
          launchOptions.args.push('--no-sandbox', '--disable-setuid-sandbox')
        }
        return launchOptions
      })

      return config
    },
  },
  env: {
    JWT_SECRET: process.env.JWT_SECRET || 'dummy-secret'
  },
  defaultCommandTimeout: 9000,
  video: true,
  pageLoadTimeout: 60000
}