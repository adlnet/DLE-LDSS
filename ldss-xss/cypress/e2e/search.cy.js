import { localLogin } from './helpers/localLogin';

describe('searchpage', () => {
    beforeEach(() => {
        cy.wait(2000)
        const url = "/admin/core/search/"

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

        cy.contains('a', 'LCV Terms').click();
    })

    it('Search by Alias', () => {
        cy.contains('Search CCV/LCV Definitions').should('be.visible')

        // Enter Search Term
        cy.get('input[name="search_term"]').type('test')

        // Toggle Search By
        cy.get('select[name="search_type"]')
          .select('Alias')
          .should('have.value', 'alias')
          
        // Select 'Search' Button
        cy.contains('button', 'Search').click()
    })

    it('Search by Definition', () => {
        // Enter search team
        cy.get('input[name="search_term"]').type('test')

        // Toggle Search By
        cy.get('select[name="search_type"]')
          .select('Definition')
          .should('have.value', 'definition')

        // Select 'Search' Button
        cy.contains('button', 'Search').click()
    })

    it('Search by Context', () => {
        // Enter search team
        cy.get('input[name="search_term"]').type('test')

        // Toggle Search By
        cy.get('select[name="search_type"]')
          .select('Context')
          .should('have.value', 'context')

        // Select 'Search' Button
        cy.contains('button', 'Search').click()
    })
})