import { localLogin } from './helpers/localLogin';

describe('relatedassignmentspage', () => {
    beforeEach(() => {
        cy.wait(2000)
        const url = "/admin/p1_auth/relatedassignment/"

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

        cy.contains('a', 'Related assignment').click();
    });

    it('Add Related Assignment +', () => {
        // Navigate to /relatedassignment/add
        cy.contains('a', 'Add related assignment').click()
        cy.contains('Add related assignment').should('be.visible')
    })

    it('Add Attribute Check', () => {
        // Navigate to /relatedassignment/add
        cy.contains('a', 'Add related assignment').click()

        // Select object model
        cy.get('.related-widget-wrapper')
          .find('select[name="object_model"]')
          .select('sessions | session')

        // Enter Object ID
        cy.get('input[name="object_pk"]').type('TestObject')

        // Confirm JWT and Expected Value Exists
        cy.get('#container #main #content-start #content #content-main form')
        cy.get('div')
        cy.get('#validators-group .tabular fieldset')
          .find('table')
          .within(() => {
            cy.contains('th', 'Jwt attribute').should('exist')
            cy.get('tbody')
              .find('td.field-jwt_attribute')
              .find('textarea[name="validators-0-jwt_attribute"]').should('exist')
            cy.contains('th', 'Expected value').should('exist')
            cy.get('tbody')
              .find('td.field-expected_value')
              .find('textarea[name="validators-0-expected_value"]').should('exist')
          })
    })

    it('Delete a JWT and Expected Value Row', () => {
        // Navigate to /relatedassignment/add
        cy.contains('a', 'Add related assignment').click()

        cy.get('#container #main #content-start #content #content-main form')
          .find('div')
          .find('#validators-group .tabular fieldset')
          .find('table')
          .find('#validators-2')
          .find('td.delete')
          .contains('a', 'Remove').click()

        // Confirm there are 2 rows now
        cy.get('#container #main #content-start #content #content-main form')
        cy.get('div')
        cy.get('#validators-group .tabular fieldset')
        cy.get('table')
        cy.get('tr[id^="validators-"]').not('.empty-form')
          .should('have.length', 2)
    })

    it('Add Another Attribute Check', () => {
        // Navigate to /relatedassignment/add
        cy.contains('a', 'Add related assignment').click()

        //Add another attribute check
        cy.get('#container #main #content-start #content #content-main form')
          .find('div')
          .find('#validators-group .tabular fieldset')
          .find('table')
          .find('tr.add-row')
          .find('td')
          .contains('a', 'Add another Attribute check').click()

        // Confirm there are 4 rows
        cy.get('#container #main #content-start #content #content-main form')
        cy.get('div')
        cy.get('#validators-group .tabular fieldset')
        cy.get('table')
        cy.get('tr[id^="validators-"]').not('.empty-form')
          .should('have.length', 4)
    })
})