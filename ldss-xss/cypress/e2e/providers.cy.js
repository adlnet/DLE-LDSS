import { localLogin } from './helpers/localLogin';

describe('providerpage', () => {
    beforeEach(() => {
        cy.wait(2000)
        const url = "/admin/uid/providerdjangomodel"

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

        cy.contains('a', 'Providers').click();
    })

    it('Add LCV Term; ADD PROVIDER +', () => {
        // Navigate to /uid/providerdjangomodel/add
        cy.contains('a', 'Add Provider').click()
        cy.contains('Add Provider').should('be.visible')
    })


    it('Add Provider; SAVE', () => {
        // Navigate to /uid/providerdjangomodel/add/
        cy.contains('a', 'Add Provider').click()
        
        // Enter Name
        cy.get('input[name="name"]').type('TestName')
 
        // (this isn't implemented yet...)
        // Select 'SAVE' input
        //cy.get('input[name="_save"]')
        //.click()
    })

    it('Add Provider; Save and continue editing', () => {
        // Navigate to /uid/providerdjangomodel/add/
        cy.contains('a', 'Add Provider').click()
        
        // Enter Name
        cy.get('input[name="name"]').type('TestName')
 
        // Select 'Save and continue editing' input
        cy.get('input[name="_continue"]')
        .click()
    })

    it('Add Provider; Save and add another', () => {
        // Navigate to /uid/providerdjangomodel/add/
        cy.contains('a', 'Add Provider').click()
        
        // Enter Name
        cy.get('input[name="name"]').type('TestName')
 
        // Select 'Save and add another' input
        cy.get('input[name="_addanother"]')
        .click()
    })

    it('Search for Provider', () => {
        cy.get('input[id="searchbar"]').type('TestName')
        cy.get('input[value="Search"]').click()

        // Confirm one entry exists (TestName)
        cy.get('#container #main #content-start #content #content-main #changelist .changelist-form-container form')
        .find('.results').should('exist')
    })

    it('Remove Provider', () => {
        cy.get('#container #main #content-start #content #content-main #changelist .changelist-form-container form')
        .find('.results')
        .find('table')
        .find('tbody')
        .find('tr')
        .each(($row) => {
            // Try to find the <td> with class 'field-name' that contains provider_name
            cy.wrap($row)
            .find('th.field-name')
            .then(($td) => {
                // If provider_name is found within the <td>, check the checkbox
                if ($td.text().includes("TestName")) {
                    cy.wrap($row)
                    .find('td.action-checkbox')
                    .find('input[type="checkbox"]')
                    .check()  // Check the checkbox (set it to true)
                }
            })        
        })

        // Select "Delete selected providers" from the drop-down menu
        cy.get('.actions')
        .find('select[name="action"]')
        .select('Delete selected Providers')
        .should('have.value', 'delete_selected')

        // Click "Go" button
        cy.get('.actions')
        .find('button[type="submit"]')  
        .click()

        // /uid/providerdjangomodel page reloads
        // Click "Yes, I'm sure" button
        cy.get('#container #main #content-start #content')
        .find('form')
        .find('div')
        .find('input[type="submit"]')
        .click()
    })
})