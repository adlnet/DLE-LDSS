import { localLogin } from './helpers/localLogin';

describe('deconflictionsection', () => {
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
          localLogin("admin@email.com", "password");
      }
    })

    it('Navigate from /admin to /deconfliction_service/deconfliction', () => {
        // Navigate to /deconfliction_service/deconfliction
        cy.get('#container #main #content-start #content #content-main .app-deconfliction_service table')
          .find('a[href$="/admin/deconfliction_service/deconfliction/"]')
          .first()
          .click()
        // Check if a specific element is visible on the dashboard
        cy.contains('Deconfliction Service').should('be.visible')
    })

    it('Navigate from /admin to /deconfliction_service/deconfliction; View button', () => {
        // Navigate to /deconfliction_service/deconfliction via View button
        cy.get('#container #main #content-start #content #content-main .app-deconfliction_service table')
          .contains('a', 'View')
          .click()
        // Check if a specific element is visible on the dashboard
        cy.contains('Deconfliction Service').should('be.visible')
    })
})