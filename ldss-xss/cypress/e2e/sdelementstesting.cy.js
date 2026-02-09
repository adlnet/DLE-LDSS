import { localLogin } from './helpers/localLogin';

const testtoken = require('../config/testToken.js');

let fileUploadAvailable = true
try {
  require('cypress-file-upload')
} catch (e) {
  fileUploadAvailable = false
  // Will still log in Cypress output
  console.warn('Warning: cypress-file-upload module not found. Upload tests may be skipped.')
}

let sd_test_url = ""
if(Cypress.env('isCI')) {
  sd_test_url = "/ldss-xss"
} else {
  sd_test_url = "/admin"
}

describe('Authed Tests', () => {
  beforeEach(() => {
    cy.wait(2000)

    // If running CI use visitWithJWT, else use completeLogin
    if (Cypress.env('isCI')) {
        const jwt = Cypress.env('adminJWT')
        if (!jwt) {
            throw new Error('JWT is missing in CI environment')
        }
        cy.visitWithJWT(sd_test_url, jwt)
    } else {
        // Call completeLogin command
        localLogin("admin@email.com", "password");
    }
  });
  
  // PASSING

  it('T99 Read-only Data Tampering', () => {
    // Visit page with hidden value
    // cy.visit(sd_test_url)

    // Locate hidden input and tamper with it (client-side)
    cy.get('#logout-form input[name="csrfmiddlewaretoken"]')
      .invoke('val', 'invalid-token-123')

    // Submit logout-form
    cy.get('#logout-form').submit()

    // Assert that the server rejected the request
    cy.contains('CSRF verification failed').should('exist')
    cy.get('h1').should('contain.text', 'Forbidden').and('contain.text', '403')
  })

  it('T99 Session Hijacking Test', () => {
    // Force-set a fake session cookie
    cy.setCookie('sessionid', 'FAKE_SESSION_ID')

    // Visit a page that requires login
    cy.visit("/admin/users/customuser/");

    //Should be redirected to login or denied
    cy.url().should('include', '/login')
  })

  
  // PASSING

  // Skip test if file upload plugin is unavailable
  if (!fileUploadAvailable) {
    it('T129 File Name Reliance - SKIPPED (missing cypress-file-upload)', () => {
      cy.log('Skipping test: cypress-file-upload module not found.')
    })
  } else {
    it('T129 File Name Reliance', () => {
      // Neoterm upload_csv()
      cy.contains('a', 'Neo term').click();
      cy.contains('a', 'CSV Upload').click()

      // Upload unacceptable file type
      cy.get('input[name="csv_file"]').attachFile('test-not-csv.txt')
      cy.get('input[name="entity_id"]').type('jko')
      cy.get('input[name="_save"]').click()

      cy.wait(2000)

      // Expect error response
      cy.contains('div', 'Invalid file type')
    })
  }

  // PASSING

  it('T89 Cookie Injection', () => {
    const payload = `javascript:alert('xss')`

    cy.setCookie('xss_test_cookie', payload)
    cy.wait(2000)
    cy.visit(sd_test_url, { failOnStatusCode: false })

    cy.document().then((doc) => {
      console.log(doc.documentElement.innerHTML)

      const html = doc.documentElement.innerHTML
      expect(html).to.not.include(payload)
      expect(html).to.not.include('alert(')
    })

    cy.on('window:alert', () => {
      throw new Error('XSS triggered via cookie!')
    })
  })

  it('T106 Direct Object Access', () => {
    // No access to files outside media root
    cy.request({
      url: '/media/../openlxp_xss_project/settings.py',
      failOnStatusCode: false,
    }).then((res) => {
      expect(res.status).to.not.eq(200)
      expect(res.body).to.not.include('MEDIA_URL')
    })
  })

  it('T332 CSP Header Validation', () => {
    cy.request(sd_test_url).then((response) => {
      const csp = response.headers['content-security-policy']

      // Check that the CSP header exists
      expect(csp, 'CSP header exists').to.exist

      // Basic policy checks
      expect(csp).to.include('default-src')
      expect(csp).to.include('form-action')
      expect(csp).to.not.include('unsafe-inline')
      expect(csp).to.not.include('unsafe-eval')
    })
  })

  it('T403 Error Message Disclosure', () => {
    cy.visit(sd_test_url + "non-existent-page", { failOnStatusCode: false })

    // Look for generic error message
    cy.contains('h1', 'Not Found')
      .should('be.visible')

    cy.get('body')
      .should('not.contain', 'Exception')
      .and('not.contain', 'StackTrace')
      .and('not.contain', '/admin') // avoid path leaks
      .and('contain', 'The requested resource was not found on this server.')
  })
})

// PASSING

describe('T89 XSS Injection Tests', () => {
  // Simulate reflected XSS in catalog results
  const payload = `<script>alert('xss')</script>`
  const encodedPayload = encodeURIComponent(payload)
  
  it('Parameter Name/Value Injection: status 200', () => {
    cy.request({
      method: 'GET',
      url: sd_test_url + `/api/catalog/?provider=${encodedPayload}`,
      failOnStatusCode: false
    }).then((response) => {
      //Payload was properly sanitized
      expect(response.status).to.eq(200)

      const body = JSON.stringify(response.body)
      expect(body).to.not.include(payload)
      expect(body).to.not.include(`<script>alert('xss')</script>`)
    })
  })

  // Simulate header injection reflected into UI
  it('HTTP Header Injection', () => {
    const payload = `' onmouseover=alert(/XSS/)`

    cy.request({
      url: sd_test_url,
      headers: {
        'X-Custom-XSS': payload
      },
      failOnStatusCode: false
    }).then((res) => {
      expect(res.status).to.be.lessThan(500)
      expect(res.body).to.not.include(payload)
    })
  })
})


const tokenGeneration = require("../util/tokenGeneration");

describe('T85 JWT and Role-claim Tests', () => {
  // Build a valid-looking JWT with an unauthorized group-full claim
  const invalidToken = testtoken.generateBadJWT()

  it('Incorrect JWT group-full value', () => {
    // Should NOT allow access to admin page with group-full claim
    cy.request({
      method: 'GET',
      url: sd_test_url + "/core/search/",
      headers: {
        Authorization: `Bearer ${invalidToken}`
      },
      failOnStatusCode: false
    }).then((res) => {
      // Backend blocks access even with valid JWT if role claim is incorrect
      expect(res.status).to.be.oneOf([400, 401, 403, 404])
      expect(res.body).to.not.contain('Site administration')
    })
  })

  it('Cannot access data', () => {
    // Should NOT allow fetching admin resources with invalid JWT group
    cy.request({
      method: 'GET',
      url: "/ldss-xss/admin/uid/lcvtermdjangomodel/",
      headers: {
        Authorization: `Bearer ${invalidToken}`
      },
      failOnStatusCode: false
    }).then((res) => {
      expect(res.status).to.be.oneOf([400, 401, 403, 404])
      expect(res.body).to.not.include('<table')
      expect(res.body).to.not.include('Select neo alias to change')
    })
  })
})

// PASSING

describe('T128 Access Control Bypass Tests', () => {
  it('Randomly Generated Session Keys', () => {
    const email = 'a@email.com'
    const testing_p = 'p'

    if (Cypress.env('isCI')) {
      const jwt = Cypress.env('adminJWT')
      if (!jwt) {
        throw new Error('JWT is missing in CI environment')
      }

      cy.visitWithJWT(sd_test_url, jwt)
      cy.getCookie('sessionid').then((cookie1) => {
        expect(cookie1).to.exist
        cy.contains('button', 'Log out').click()
        cy.contains('a', 'Log in again').click()

        cy.visitWithJWT(sd_test_url, jwt)
        cy.getCookie('sessionid').then((cookie2) => {
          expect(cookie2).to.exist
          expect(cookie1.value).to.not.equal(cookie2.value)
        })
      })

    } else {
      // First login
      cy.visit(sd_test_url)
      cy.get('input[name="username"]').type(email)
      cy.get('input[name="password"]').type(testing_p)
      cy.get('input[value="Log in"]').click()

      cy.getCookie('sessionid').then((cookie1) => {
        expect(cookie1).to.exist
        cy.contains('button', 'Log out').click()
        cy.contains('a', 'Log in again').click()

        // Second login
        cy.visit(sd_test_url)
        cy.get('input[name="username"]').type(email)
        cy.get('input[name="password"]').type(testing_p)
        cy.get('input[value="Log in"]').click()

        cy.getCookie('sessionid').then((cookie2) => {
          expect(cookie2).to.exist
          expect(cookie1.value).to.not.equal(cookie2.value)
        })
      })
    }
  })
})

// PASSING

describe('T98 Input Validation Tests', () => {
  it('Valid Base Endpoint', () => {
    cy.request({
      method: 'GET',
      url: sd_test_url + "/catalog/all/?provider=jko",
      failOnStatusCode: false
    }).then((res) => {
      const body = typeof res.body === 'object' ? JSON.stringify(res.body) : res.body
      const errorSnippet = 'No catalogs found for the specified provider.'

      if (body.includes(errorSnippet)) {
        cy.log('Catalog not found for provider; skipping status check')
      } else {
        expect(res.status).to.eq(200)
      }
    })
  })

  // PASSING

  const invalidProviders = [
    '',             // empty string
    'undefined',    // string "undefined"
    '<script>',     // XSS test (SD Element T89)
    '../../../etc', // path traversal (SD Element T106)
    "' OR '1'='1"   // SQL injection
  ]

  invalidProviders.forEach((invalidValue) => {
    it(`Invalid Provider: "${invalidValue}"`, () => {
      cy.request({
        method: 'GET',
        url: sd_test_url + "/catalog/all/?provider=${encodeURIComponent(invalidValue)}",
        failOnStatusCode: false
      }).then((res) => {
        // Either reject or safely ignore
        expect(res.status).to.be.oneOf([400, 422, 404, 200])
      })
    })
  })
})

// PASSING

describe('113 HTTP Verb Tampering', () => {
  it('T113 HEAD Request Fails if GET Fails', () => {
    // Attempt unauthenticated GET
    cy.request({
      method: 'GET',
      url: sd_test_url,
      failOnStatusCode: false
    }).then((getRes) => {
      // Attempt HEAD
      cy.request({
        method: 'HEAD',
        url: sd_test_url,
        failOnStatusCode: false
      }).then((headRes) => {
        // If GET is blocked, then HEAD also blocked
        if(getRes.status !== 200) {
          expect(headRes.status).to.not.eq(200)
        }
      })
    })
  })
})

// PASSING

describe('T112 Cache Control for Confidential Pages', () => {
  it('Check for Appropriate Cache-control Headers', () => {
    cy.request({
      url: sd_test_url + "/users", // confidential page
      failOnStatusCode: false
    }).then((response) => {
      const headers = response.headers

      // Must have no-store, no-cache, must-revalidate
      expect(headers).to.have.property('cache-control')
      expect(headers['cache-control']).to.include('no-store')
      expect(headers['cache-control']).to.include('no-cache')
      expect(headers['cache-control']).to.include('must-revalidate')

      expect(headers).to.have.property('expires')
      expect(headers['expires']).to.satisfy((value) =>
        value === '-1' || new Date(value) <= new Date()
      )
    })
  })
})

// PASSING

describe('T132 Character Set Declaration (UTF-8', () => {
  const pagesToTest = [
    "/",
    sd_test_url,
    sd_test_url + "/core"
  ]

  pagesToTest.forEach((url) => {
    it(`Declare UTF-8 charset on ${url}`, () => {
      cy.request(url).then((response) => {
        const headers = response.headers
        const contentType = headers['content-type'] || ''
        const html = response.body

        const charsetInHeader = contentType.toLowerCase().includes('charset=utf-8')
        const charsetInMeta = /<meta\s+[^>]*charset=["']?utf-8["']?/i.test(html)

        expect(
          charsetInHeader || charsetInMeta,
          `Charset not declared on ${url}`
        ).to.be.true
      })
    })
  })
})
