import { localLogin } from './helpers/localLogin';

describe('corepage', () => {
    beforeEach(() => {
        cy.wait(2000);
        const url = "/admin/core";

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

    // CCV Upstreams
    it('Navigate from /core to /core/ccvupstream', () => {
        // Navigate to /core/ccvupstream
        cy.get('#container #main #content-start #content #content-main .app-core table')
          .contains('a', 'Ccv upstreams')
          .click()
        cy.contains('Select ccv upstream to change').should('be.visible')
    })

    it('Navigate from /core to /core/ccvupstream/add; Add button', () => {
      // Navigate to /uid/lcvtermdjangomodel/add via '+ Add' button
      cy.get('#container #main #content-start #content #content-main .app-core table')
        .find('a[href$="/admin/core/ccvupstream/add/"]')
        .click()
      // Check if a specific element is visible on the dashboard
      cy.contains('Add ccv upstream').should('be.visible')
    })

    it('Navigate from /core to /core/ccvupstream; Change button', () => {
        // Navigate to /core/ccvupstream via 'Change' button
        cy.get('#container #main #content-start #content #content-main .app-core table')
          .find('a[href$="/admin/core/ccvupstream/"]')
          .eq(1)
          .click()
        // Check if a specific element is visible on the dashboard
        cy.contains('Select ccv upstream to change').should('be.visible')
    })

    // LCV Downstreams
    it('Navigate from /core to /core/lcvdownstream', () => {
        // Navigate to /core/lcvdownstream
        cy.get('#container #main #content-start #content #content-main .app-core table')
        .contains('a', 'Lcv downstreams')
        .click()
        cy.contains('Select lcv downstream to change').should('be.visible')
    })

    it('Navigate from /core to /core/lcvdownstream/add; Add button', () => {
    // Navigate to /core/lcvdownstream/add via '+ Add' button
    cy.get('#container #main #content-start #content #content-main .app-core table')
        .find('a[href$="/admin/core/lcvdownstream/add/"]')
        .click()
    // Check if a specific element is visible on the dashboard
    cy.contains('Add lcv downstream').should('be.visible')
    })

    it('Navigate from /core to /core/lcvdownstream; Change button', () => {
        // Navigate to /core/lcvdownstream via 'Change' button
        cy.get('#container #main #content-start #content #content-main .app-core table')
        .find('a[href$="/admin/core/lcvdownstream/"]')
        .eq(1)
        .click()
        // Check if a specific element is visible on the dashboard
        cy.contains('Select lcv downstream to change').should('be.visible')
    })

// Neo Alias
    it('Navigate from /core to /core/neoalias', () => {
        // Navigate to /core/neoalias
        cy.get('#container #main #content-start #content #content-main .app-core table')
        .contains('a', 'Neo aliass')
        .click()
        cy.contains('Select neo alias to change').should('be.visible')
    })

    it('Navigate from /core to /core/neoalias/add; Add button', () => {
    // Navigate to /core/neoalias/add via '+ Add' button
    cy.get('#container #main #content-start #content #content-main .app-core table')
        .find('a[href$="/admin/core/neoalias/add/"]')
        .click()
    // Check if a specific element is visible on the dashboard
    cy.contains('Add neo alias').should('be.visible')
    })

    it('Navigate from /core to /core/neoalias; Change button', () => {
        // Navigate to /core/neoalias via 'Change' button
        cy.get('#container #main #content-start #content #content-main .app-core table')
        .find('a[href$="/admin/core/neoalias/"]')
        .eq(1)
        .click()
        // Check if a specific element is visible on the dashboard
        cy.contains('Select neo alias to change').should('be.visible')
    })

// Neo Contexts
    it('Navigate from /core to /core/neocontext', () => {
        // Navigate to /core/neocontext
        cy.get('#container #main #content-start #content #content-main .app-core table')
        .contains('a', 'Neo context')
        .click()
        cy.contains('Select neo context to change').should('be.visible')
    })

    it('Navigate from /core to /core/neocontext/add; Add button', () => {
    // Navigate to /core/neocontext/add via '+ Add' button
    cy.get('#container #main #content-start #content #content-main .app-core table')
        .find('a[href$="/admin/core/neocontext/add/"]')
        .click()
    // Check if a specific element is visible on the dashboard
    cy.contains('Add neo context').should('be.visible')
    })

    it('Navigate from /core to /core/neocontext; Change button', () => {
        // Navigate to /core/neocontext via 'Change' button
        cy.get('#container #main #content-start #content #content-main .app-core table')
        .find('a[href$="/admin/core/neocontext/"]')
        .eq(1)
        .click()
        // Check if a specific element is visible on the dashboard
        cy.contains('Select neo context to change').should('be.visible')
    })

// Neo definitions
    it('Navigate from /core to /core/neodefinition', () => {
        // Navigate to /core/neodefinition
        cy.get('#container #main #content-start #content #content-main .app-core table')
        .contains('a', 'Neo definitions')
        .click()
        cy.contains('Select neo definition to change').should('be.visible')
    })

    it('Navigate from /core to /core/neodefinition/add; Add button', () => {
    // Navigate to /core/neodefinition/add via '+ Add' button
    cy.get('#container #main #content-start #content #content-main .app-core table')
        .find('a[href$="/admin/core/neodefinition/add/"]')
        .click()
    // Check if a specific element is visible on the dashboard
    cy.contains('Add neo definition').should('be.visible')
    })

    it('Navigate from /core to /core/neodefinition; Change button', () => {
        // Navigate to /core/neodefinition via 'Change' button
        cy.get('#container #main #content-start #content #content-main .app-core table')
        .find('a[href$="/admin/core/neodefinition/"]')
        .eq(1)
        .click()
        // Check if a specific element is visible on the dashboard
        cy.contains('Select neo definition to change').should('be.visible')
    })

// Neo terms
    it('Navigate from /core to /core/neoterm', () => {
        // Navigate to /core/neoterm
        cy.get('#container #main #content-start #content #content-main .app-core table')
        .contains('a', 'Neo terms')
        .click()
        cy.contains('Select neo term to change').should('be.visible')
    })

    it('Navigate from /core to /core/neoterm/add; Add button', () => {
    // Navigate to /core/neoterm/add via '+ Add' button
    cy.get('#container #main #content-start #content #content-main .app-core table')
        .find('a[href$="/admin/core/neoterm/add/"]')
        .click()
    // Check if a specific element is visible on the dashboard
    cy.contains('Add neo term').should('be.visible')
    })

    it('Navigate from /core to /core/neoterm; Change button', () => {
        // Navigate to /core/neoterm via 'Change' button
        cy.get('#container #main #content-start #content #content-main .app-core table')
        .find('a[href$="/admin/core/neoterm/"]')
        .eq(1)
        .click()
        // Check if a specific element is visible on the dashboard
        cy.contains('Select neo term to change').should('be.visible')
    })

//Search
    it('Navigate from /core to /core/search', () => {
        // Navigate to /core/search
        cy.get('#container #main #content-start #content #content-main .app-core table')
        .contains('a', 'Search')
        .click()
        cy.contains('Search CCV/LCV Definitions').should('be.visible')
    })

    it('Navigate from /core to /core/search/add; Add button', () => {
    // Navigate to /core/search/add via '+ Add' button
    cy.get('#container #main #content-start #content #content-main .app-core table')
        .find('a[href$="/admin/core/search/add/"]')
        .click()
    // Check if a specific element is visible on the dashboard
    cy.contains('Add search').should('be.visible')
    })

    it('Navigate from /core to /core/search; Change button', () => {
        // Navigate to /core/search via 'Change' button
        cy.get('#container #main #content-start #content #content-main .app-core table')
        .find('a[href$="/admin/core/search/"]')
        .eq(1)
        .click()
        // Check if a specific element is visible on the dashboard
        cy.contains('Search CCV/LCV Definitions').should('be.visible')
    })
})