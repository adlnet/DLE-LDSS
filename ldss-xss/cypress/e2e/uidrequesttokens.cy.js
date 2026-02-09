import { localLogin } from './helpers/localLogin';

describe('uidrequesttokenpage', () => {
    beforeEach(() => {
        cy.wait(2000)
        const url = "/admin/uid/uidrequesttoken"

        // If running CI use visitWithJWT, else use completeLogin
        if (Cypress.env('isCI')) {
            const jwt = Cypress.env('adminJWT')
            if (!jwt) {
                throw new Error('JWT is missing in CI environment')
            }
            cy.visitWithJWT(url, jwt)
        } else {
          localLogin("admin@email.com", "password");
        }
        cy.contains('a', 'UIDRequestToken').click();
    })

    it('Add LCV Term; ADD UIDREQUESTTOKEN +', () => {
        // Navigate to /uid/uidrequesttoken/add
        cy.contains('a', 'Add UIDRequestToken').click()
        cy.contains('Add UIDRequestToken').should('be.visible')
    })

    it('Add UIDRequestToken; SAVE', () => {
        // Navigate to /uid/uidrequesttoken/add/
        cy.contains('a', 'Add UIDRequestToken').click()
        
        // Enter Name
        cy.get('input[name="provider_name"]').type('TestToken')
 
    });

    it('Add UIDRequestToken; DELETE', () => {
        // Navigate to /uid/uidrequesttoken/add/
        cy.contains('a', 'Add UIDRequestToken').click()
        
        // Enter Name
        cy.get('input[name="provider_name"]').type('TestToken')
 
        // (this isn't implemented yet...)
        // Select 'SAVE' input
        //cy.get('input[name="_save"]')
        //.click()
    })
})