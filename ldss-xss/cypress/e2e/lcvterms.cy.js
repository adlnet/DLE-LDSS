import { localLogin } from './helpers/localLogin';

describe('lcvtermpage', () => {
    beforeEach(() => {
        cy.wait(2000)
        const url = "/admin/uid/lcvtermdjangomodel"

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

    it('Add LCV Term; ADD LCV TERM +', () => {
        // Navigate to /uid/lcvtermdjangomodel/add
        cy.contains('a', 'Add LCV Term').click()
        cy.contains('Add LCV Term').should('be.visible')
    })

    it('Add LCV Term; SAVE', () => {
        // Navigate to /uid/lcvtermdjangomodel/add
        cy.contains('a', 'Add LCV Term').click()
        
        // Enter Provider name
        cy.get('input[name="provider_name"]').type('TestSource')

        // Enter Term
        cy.get('input[name="term"]').type('Test')

        // Enter Echelon
        cy.get('input[name="echelon"]').type('Teschelon')

        // Enter Structure
        cy.get('input[name="structure"]').type('Testure')
 
        // Can't select SAVE/Save and continue editing/ Save and add another
        // (this isn't implemented yet...)
        // Select 'SAVE' input
        //cy.get('input[name="_save"]')
        //.click()
    })

    it('Search for LCV Term', () => {
        // Search available groups
        cy.get('input[id="searchbar"]').type('Test')
        cy.get('input[value="Search"]').click()
    })
})