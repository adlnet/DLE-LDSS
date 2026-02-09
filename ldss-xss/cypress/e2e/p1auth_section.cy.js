import { localLogin } from './helpers/localLogin';

describe('p1authsection', () => {
    beforeEach(() => {
      cy.wait(2000)

      // If running CI use visitWithJWT, else use completeLogin
      if (Cypress.env('isCI')) {
        const jwt = Cypress.env('adminJWT')
        if (!jwt) {
          throw new Error('JWT is missing in CI environment')
        }
        cy.visitWithJWT("/admin", jwt)
      } else {
        // Call completeLogin command
        localLogin("admin@email.com", "password");
      }
    })

    it('Navigate from /admin to /attributecheck; Change button', () => {
        // Navigate to /attributecheck via 'Change' button
        cy.get('#container #main #content-start #content #content-main .app-p1_auth table')
          .find('a[href$="/admin/p1_auth/attributecheck/"]')
          .eq(1)
          .click()
        // Check if a specific element is visible on the dashboard
        cy.contains('Select attribute check to change').should('be.visible')
    })

    it('Navigate from /admin to /attributecheck/add/; Add button', () => {
        // Navigate to /attributecheck/add/ via '+ Add' button
        cy.get('#container #main #content-start #content #content-main .app-p1_auth table')
          .find('a[href$="/admin/p1_auth/attributecheck/add/"]')
          .click()
        // Check if a specific element is visible on the dashboard
        cy.contains('Add attribute check').should('be.visible')
    })


    it('Navigate from /admin to /relatedassignment', () => {
        // Navigate to /relatedassignment
        cy.contains('a', 'Related assignments').click()
        cy.contains('Select related assignment to change').should('be.visible')
    })

    it('Navigate from /admin to /relatedassignment/add/; Add button', () => {
        // Navigate to /relatedassignment/add via '+ Add' button
        cy.get('#container #main #content-start #content #content-main .app-p1_auth table')
          .find('a[href$="/admin/p1_auth/relatedassignment/add/"]')
          .click()
        // Check if a specific element is visible on the dashboard
        cy.contains('Add related assignment').should('be.visible')
    })

    it('Navigate from /admin to /relatedassignment; Change button', () => {
        // Navigate to /relatedassignment via 'Change' button
        cy.get('#container #main #content-start #content #content-main .app-p1_auth table')
          .find('a[href$="/admin/p1_auth/relatedassignment/"]')
          .eq(1)
          .click()
        // Check if a specific element is visible on the dashboard
        cy.contains('Select related assignment to change').should('be.visible')
    })
})