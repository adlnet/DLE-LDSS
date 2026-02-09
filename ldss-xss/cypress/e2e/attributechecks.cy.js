import { localLogin } from './helpers/localLogin';

describe('attributecheckspage', () => {
    beforeEach(() => {
        cy.wait(2000)
        const url = "/admin/p1_auth/attributecheck/"

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

    it('Add Attribute Check +', () => {
        // Navigate to /attributecheck/add
        cy.contains('a', 'Attribute checks').click();
        cy.contains('a', 'Add attribute check').click();
        cy.contains('Add attribute check').should('be.visible')
    })

    it('Add Attribute Check', () => {
        // Navigate to /attributecheck/add
        cy.contains('a', 'Attribute checks').click();
        
        cy.contains('a', 'Add attribute check').click()
        
        // Enter Jwt attribute:
        cy.get('textarea[name="jwt_attribute"]')
          .invoke('val')
          .should('eq', 'null')

        // Enter Expected value
        cy.get('textarea[name="expected_value"]')
          .invoke('val')
          .should('eq', 'null')

        // Select Assignment
        cy.get('.related-widget-wrapper')
          .find('select[name="assignment"]')
          .select('---------')
          .should('have.value', '')

        // Confirm "change selected related assignment" button exists
        cy.get('img[alt="Change"]')
          .should('be.visible')

        // Confirm "add another related assignment" button exists
        cy.get('img[alt="Add"]')
          .should('be.visible')

        // Confirm "view selected related assignment" button exists
        cy.get('img[alt="View"]')
          .should('be.visible')
    })
})