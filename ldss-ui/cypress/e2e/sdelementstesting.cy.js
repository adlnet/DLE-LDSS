/// <reference types="Cypress" />

const testtoken = require('../support/testToken.js');

it('T89 Cookie Injection', () => {
  const payload = `javascript:alert('xss')`
  cy.setCookie('xss_test_cookie', payload)

  cy.request({
    url: '/',
    headers: {
      'x-cypress-test': 'true',
    },
    failOnStatusCode: false,
  }).then((resp) => {
    const html = resp.body
    console.log(html)

    expect(html).to.not.include(payload)
    expect(html).to.not.include('alert(')
  })

  cy.on('window:alert', () => {
    throw new Error('XSS triggered via cookie!')
  })
})

it('T99 Tampering with CSRF token is rejected', () => {
  // Initialize cookies by hitting the base URL
  cy.request({
    url: '/',
    headers: {
      'x-cypress-test': 'true',
    },
  }).then(() => {
    // Overwrite the CSRF token with a fake one
    cy.setCookie('csrftoken', 'FAKE_CSRF_TOKEN')

    cy.request({
      method: 'POST',
      url: '/admin',
      body: { some: 'data' },
      headers: {
        'X-CSRFToken': 'FAKE_CSRF_TOKEN',
        'x-cypress-test': 'true',
      },
      failOnStatusCode: false,
    }).then((res) => {
      // Expect the server to reject the request
      expect([403, 400, 404]).to.include(res.status)
    })
  })
})

const suspiciousPaths = [
'/data/../../package.json',
'/api/../../src/secrets.ts',
'/../.env',
'/../README.md',
'/../../../etc/passwd',
]
suspiciousPaths.forEach((path) => {
  it(`T106 Block Access to Suspicious Paths`, () => {
    cy.request({
      url: path,
      headers: {
        'x-cypress-test': 'true',
      },
      failOnStatusCode: false
    }).then((res) => {
      expect(res.status).to.not.eq(200);
      expect(res.body).to.not.include('PRIVATE_KEY')
      expect(res.body).to.not.include('root:')
    })
  })
})

const internalFiles = [
  '/src/config.ts',
  '/env/.env',
  '/logs/app.log',
]
internalFiles.forEach((file) => {
  it(`T106 No Access to Internal Files`, () => {
    cy.request({
      url: file,
      headers: {
        'x-cypress-test': 'true',
      },
      failOnStatusCode: false
    }).then((res) => {
      expect(res.status).to.not.eq(200)
    })
  })
})

it('T403 Error Message Disclosure', () => {
  cy.request({
    url: '/non-existent-page',
    headers: {
      'x-cypress-test': 'true',
    },
    failOnStatusCode: false,
  }).then((res) => {
    const html = res.body

    expect(html).to.include('404')

    expect(html).to.not.include('Exception')
    expect(html).to.not.include('StackTrace')
    expect(html).to.not.include('/admin')
    expect(html).to.include('This page could not be found.')
  })
})

describe('T128 Access Control Bypass', () => {
  it('Spoof Headers', () => {
    const spoofedJWT = 'eyFake.JWT.with.admin.claim'

    cy.request({
      url: '/api/headers',
      headers: {
        Authorization: `Bearer ${spoofedJWT}`,
        'x-istio-jwt-assertion': spoofedJWT,
        'sec-istio-auth-userinfo': 'fake-user-info',
        'x-cypress-test': 'true',
      },
      failOnStatusCode: false,
    }).then((res) => {
      // Confirm server simply echoes headers, but doesn't grant access
      expect(res.status).to.eq(200)

      expect(res.body).to.not.have.property('x-access-level', 'admin')
      expect(res.body).to.not.have.property('x-user-role', 'admin')
    })
  })
})

describe('T89 XSS Injection Tests', () => {
  // Simulate header injection reflected into UI
  it('HTTP Header Injection', () => {
    const payload = `' onmouseover=alert(/XSS/)`

    cy.request({
      url: '/',
      headers: {
        'X-Custom-XSS': payload,
        'x-cypress-test': 'true',
      },
      failOnStatusCode: false,
    }).then((res) => {
      expect(res.status).to.be.lessThan(500)
      expect(res.body).to.not.include(payload)
    })
  })
})

describe('T128 Access Control via Mapped Terms Inputs', () => {
  it('Should block unauthorized source/target values', () => {
    const invalidValues = ['secret-source', 'hidden', 'admin-db']

    invalidValues.forEach((val) => {
      cy.request({
        url: `/api/mapped-terms?source=${encodeURIComponent(val)}&target=aetc`,
        headers: {
          'x-cypress-test': 'true',
        },
        failOnStatusCode: false,
      }).then((res) => {
        expect(res.status).to.eq(400);
        expect(res.body).to.have.property('error');
        expect(res.body.error).to.include('Invalid');
      })
    })
  })

  it('Should block missing source/target', () => {
    cy.request({
      url: `/api/mapped-terms?source=aetc`,
      headers: {
        'x-cypress-test': 'true',
      },
      failOnStatusCode: false,
    }).then((res) => {
      expect(res.status).to.eq(400);
      expect(res.body).to.have.property('error')
    })
  })
})

describe('T98 Server-side Input Validation', () => {
  const validSource = 'aetc'
  const validTarget = 'jko'

  const invalidValues = ['<script>', 'DROP TABLE', 'admin', '1234', '', ' ']

  invalidValues.forEach((invalidInput) => {
    it(`Should reject invalid source: "${invalidInput}"`, () => {
      cy.request({
        url: `/api/mapped-terms?source=${encodeURIComponent(invalidInput)}&target=${encodeURIComponent(validTarget)}`,
        headers: {
          'x-cypress-test': 'true',
        },
        failOnStatusCode: false,
      }).then((res) => {
        expect(res.status).to.eq(400);
        expect(res.body).to.have.property('error')
        expect(res.body.error).to.include('Invalid')
      })
    })

    it(`Should reject invalid target: "${invalidInput}"`, () => {
      cy.request({
        url: `/api/mapped-terms?source=${encodeURIComponent(validSource)}&target=${encodeURIComponent(invalidInput)}`,
        headers: {
          'x-cypress-test': 'true',
        },
        failOnStatusCode: false,
      }).then((res) => {
        expect(res.status).to.eq(400);
        expect(res.body).to.have.property('error')
        expect(res.body.error).to.include('Invalid')
      })
    })
  })
})

describe('113 HTTP Verb Tampering', () => {
  it('T113 HEAD Request Fails if GET Fails', () => {
    // Attempt unauthenticated GET
    cy.request({
      method: 'GET',
      url: '/table',
      headers: {
        'x-cypress-test': 'true',
      },
      failOnStatusCode: false,
    }).then((getRes) => {
      // Attempt HEAD
      cy.request({
        method: 'HEAD',
        url: '/table', // baseUrl automatically prepended
        headers: {
          'x-cypress-test': 'true',
        },
        failOnStatusCode: false,
      }).then((headRes) => {
        // If GET is blocked, then HEAD also blocked
        if(getRes.status !== 200) {
          expect(headRes.status).to.not.eq(200)
        }
      })
    })
  })
})

describe('T85 JWT and Role-claim Tests', () => {
  const invalidClaims = [
    undefined,
    [],
    ['invalid-group'],
  ]

  invalidClaims.forEach((claim) => {
    it(`Incorrect JWT group-full claim: ${JSON.stringify(claim)}`, () => {
      const token = testtoken.generateBadJWT(claim)

      cy.request({
        method: 'GET',
        url: `/table?nocache=${Date.now()}`,
        headers: {
          Authorization: `Bearer ${token}`,
        },
        failOnStatusCode: false,
      }).then((res) => {
        expect(res.status).to.be.oneOf([400, 401, 403, 404])
      })
    })
  })

  invalidClaims.forEach((claim) => {
    it(`Cannot access data: ${JSON.stringify(claim)}`, () => {
      const token = testtoken.generateBadJWT(claim)

      cy.request({
        method: 'GET',
        url: `/table?nocache=${Date.now()}`,
        headers: {
          Authorization: `Bearer ${token}`,
        },
        failOnStatusCode: false
      }).then((res) => {
        expect(res.status).to.be.oneOf([400, 401, 403, 404])
        expect(res.body).to.not.include('<table')
        expect(res.body).to.not.include('Source Alias')
      })
    })
  })
})

describe('T112 Cache Control for Confidential Pages', () => {
  it('T112 Confidential Pages Have No-Store Cache Headers', () => {
    const token = testtoken.generateLocalJWT('admin-user', 'e2eadmin', 'admin@email.com', Cypress.env('JWT_SECRET'));

    cy.request({
      url: `/table?nocache=${Date.now()}`,
      headers: {
        Authorization: `Bearer ${token}`,
        'x-cypress-test': 'true',
      },
      failOnStatusCode: false,
    }).then((res) => {
      expect(res.status).to.eq(200, `Expected 200 OK but got ${res.status}`)
      
      const cacheControl = res.headers['cache-control'] || ''
      const pragma = res.headers['pragma'] || ''
      const expires = res.headers['expires'] || ''

      // Must include 'no-store' in Cache-Control
      expect(cacheControl).to.include('no-store')
      expect(cacheControl).to.include('must-revalidate')

      // Optional legacy headers
      expect(pragma).to.match(/no-cache|^$/)
      expect(expires).to.match(/0|-1|^$/)
    })
  })
})

describe('T332 CSP Header Validation', () => {
  const token = testtoken.generateLocalJWT('admin-user', 'e2eadmin', 'admin@email.com', Cypress.env('JWT_SECRET'));

  it('CSP headers on /table', () => {
    cy.request({
      url: `/table?nocache=${Date.now()}`,
      headers: {
        Authorization: `Bearer ${token}`,
        'x-cypress-test': 'true',
      },
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(200, `Expected 200 OK but got ${response.status}`)

      const csp = response.headers['content-security-policy']

      // Check that the CSP header exists
      expect(csp, 'CSP header exists').to.exist

      // Basic policy checks
      expect(csp).to.include('default-src')
      expect(csp).to.include('form-action')
      expect(csp).to.not.include('unsafe-inline')
      if (Cypress.env('NODE_ENV') === 'production') {
        expect(csp).to.not.include('unsafe-eval')
      }
    })
  })
})

describe('T132 Character Set Declaration (UTF-8)', () => {
  const token = testtoken.generateLocalJWT('admin-user', 'e2eadmin', 'admin@email.com', Cypress.env('JWT_SECRET'));
  
  const pagesToTest = [
    '/',
    `/table?nocache=${Date.now()}`,
  ]

  pagesToTest.forEach((path) => {
    it(`Declare UTF-8 charset on ${path}`, () => {
      cy.request({
        url: path,
        headers: {
          Authorization: `Bearer ${token}`,
          'x-cypress-test': 'true',
        },
        failOnStatusCode: false,
      }).then((response) => {
        expect(response.status).to.eq(200, `Expected 200 OK but got ${response.status}`)

        const headers = response.headers
        const html = response.body

        const rawContentType = headers['content-type']
        const contentType = Array.isArray(rawContentType)
          ? rawContentType[0]
          : rawContentType || ''

        const charsetInHeader = contentType.toLowerCase().includes('charset=utf-8')
        const charsetInMeta = /<meta\s+[^>]*charset=["']?utf-8["']?/i.test(html)

        expect(
          charsetInHeader || charsetInMeta,
          `Charset not declared on ${path}`
        ).to.be.true
      })
    })
  })
})
