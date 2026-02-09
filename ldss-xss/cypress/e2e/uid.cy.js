import { localLogin } from './helpers/localLogin';

describe('uidpage', () => {
    beforeEach(() => {
        cy.wait(2000)
        const url = "/admin/uid/"

        // If running CI use visitWithJWT, else use completeLogin
        if (Cypress.env('isCI')) {
            const jwt = Cypress.env('adminJWT')
            if (!jwt) {
                throw new Error('JWT is missing in CI environment')
            }
            cy.visitWithJWT(url, jwt)
        } else {
            // Call completeLogin command
          localLogin("admin@email.com", "password");
        }
    })

    it('Navigate from /uid to /lcvtermdjangomodel', () => {
        // Navigate to /lcvtermdjangomodel
        cy.contains('a', 'LCV Terms').click()
        cy.contains('Select LCV Term to change').should('be.visible')
    })

    it('Navigate from /uid to /uid/lcvtermdjangomodel/add; Add button', () => {
        // Navigate to /uid/lcvtermdjangomodel/add via '+ Add' button
        cy.get('#container #main #content-start #content #content-main .app-uid table')
          .find('a[href$="/admin/uid/lcvtermdjangomodel/add/"]')
          .click()
        // Check if a specific element is visible on the dashboard
        cy.contains('Add LCV Term').should('be.visible')
    })

    it('Navigate from /uid to /uid/lcvtermdjangomodel; Change button', () => {
        // Navigate to /uid/lcvtermdjangomodel via 'Change' button
        cy.get('#container #main #content-start #content #content-main .app-uid table')
          .find('a[href$="/admin/uid/lcvtermdjangomodel/"]')
          .eq(1)
          .click()
        // Check if a specific element is visible on the dashboard
        cy.contains('Select LCV Term to change').should('be.visible')
    })

    it('Navigate from /uid to /providerdjangomodel', () => {
        // Navigate to /providerdjangomodel
        cy.contains('a', 'Providers').click()
        cy.contains('Select Provider to change').should('be.visible')
    })

    it('Navigate from /uid to /uid/providerdjangomodel/add; Add button', () => {
        // Navigate to /uid/providerdjangomodel/add via '+ Add' button
        cy.get('#container #main #content-start #content #content-main .app-uid table')
          .find('a[href$="/admin/uid/providerdjangomodel/add/"]')
          .click()
        // Check if a specific element is visible on the dashboard
        cy.contains('Add Provider').should('be.visible')
    })

    it('Navigate from /uid to /uid/providerdjangomodel; Change button', () => {
        // Navigate to /uid/providerdjangomodel via 'Change' button
        cy.get('#container #main #content-start #content #content-main .app-uid table')
          .find('a[href$="/admin/uid/providerdjangomodel/"]')
          .eq(1)
          .click()
        // Check if a specific element is visible on the dashboard
        cy.contains('Select Provider to change').should('be.visible')
    })

    it('Navigate from /uid to /uidrequesttoken', () => {
        // Navigate to /uidrequesttoken
        cy.contains('a', 'UIDRequestTokens').click()
        cy.contains('Select UIDRequestToken to change').should('be.visible')
    })

    it('Navigate from /uid to /uid/uidrequesttoken/add/; Add button', () => {
        // Navigate to /uid/uidrequesttoken/add/ via '+ Add' button
        cy.get('#container #main #content-start #content #content-main .app-uid table')
          .find('a[href$="/admin/uid/uidrequesttoken/add/"]')
          .click()
        // Check if a specific element is visible on the dashboard
        cy.contains('Add UIDRequestToken').should('be.visible')
    })

    it('Navigate from /uid to /uid/uidrequesttoken; Change button', () => {
        // Navigate to /uid/uidrequesttoken via 'Change' button
        cy.get('#container #main #content-start #content #content-main .app-uid table')
          .find('a[href$="/admin/uid/uidrequesttoken/"]')
          .eq(1)
          .click()
        // Check if a specific element is visible on the dashboard
        cy.contains('Select UIDRequestToken to change').should('be.visible')
    })
})