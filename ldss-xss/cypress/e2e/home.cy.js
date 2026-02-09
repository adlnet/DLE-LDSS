import { localLogin } from './helpers/localLogin';

describe('homepage', () => {
  beforeEach(() => {
    cy.wait(2000)

    // If running CI use visitWithJWT, else use completeLogin
    if (Cypress.env('isCI')) {
      const jwt = Cypress.env('adminJWT')
      if (!jwt) {
        throw new Error('JWT is missing in CI environment')
      }
      cy.visitWithJWT("/ldss-xss/admin", jwt)
    } else {
      // Call completeLogin command
      // cy.visit("/admin");
      localLogin("admin@email.com", "password");
    }
  })

  // Test for standard encoding format for all HTML content https://sdelements.il2.dso.mil/bunits/platform1/ecc/openlxp-xds/tasks/phase/testing/395-T132/
  it('Check content-type headers', () => {
    cy.request('/admin').as('resp')
    cy.get('@resp').its('headers').its('content-type')
      .should('include', 'text/html; charset=utf-8')
  });

// CORE
  it('Navigate from /admin to /core', () => {
    // Navigate to /core
    cy.contains('a', 'Core').click()
    cy.contains('Core administration').should('be.visible')
  })

// DECONFLICTION_SERVICE
  it('Navigate from /admin to /deconfliction_service', () => {
    // Navigate to /deconfliction_service
    cy.contains('a', 'Deconfliction_Service').click()
    cy.contains('Deconfliction_Service administration').should('be.visible')
  })

// P1_AUTH
  it('Navigate from /admin to /p1_auth', () => {
    // Navigate to /p1_auth
    cy.contains('a', 'P1_Auth').click()
    cy.contains('P1_Auth administration').should('be.visible')
  })

// UID
  it('Navigate from /admin to /uid', () => {
    // Navigate to /uid
    cy.contains('a', 'Uid').click()
    cy.contains('Uid administration').should('be.visible')
  })

// USERS
  it('Navigate from /admin to /users', () => {
    // Navigate to admin/users/
    cy.contains('a', 'Users').click()
    cy.contains('Users administration').should('be.visible')
  })
});

