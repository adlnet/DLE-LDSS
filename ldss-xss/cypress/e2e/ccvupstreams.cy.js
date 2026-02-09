import { localLogin } from './helpers/localLogin';

describe('ccvupstreamspage', () => {
    beforeEach(() => {
        cy.wait(2000)
        const url = "/admin/core/ccvupstream/"

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

    it('Add CCV Upstream +', () => {
        // Navigate to /core/ccvupstream/add
        cy.contains('a', 'Ccv upstreams').click();
        cy.contains('a', 'Add ccv upstream').click()
        cy.contains('Add ccv upstream').should('be.visible')
    })

    it('Add CCV Upstream; SAVE', () => {
        // Navigate to /core/ccvupstream/add
        cy.contains('a', 'Ccv upstreams').click();
        cy.contains('a', 'Add ccv upstream').click()

        // Enter CCV API Endpoint
        cy.get('input[name="ccv_api_endpoint"]').type('tests/test')

        // Select CCV API Endpoint Status
        cy.get('select[name="ccv_api_endpoint_status"]')
          .select('Active')
          .should('have.value', 'ACTIVE')
          .select('Inactive')
          .should('have.value', 'INACTIVE')

        // Enter CCV API Username
        cy.get('input[name="ccv_api_username"]').type('tester')

        // Enter CCV API Password
        cy.get('input[name="ccv_api_password"]').type('p')

        // Enter CCV API Key
        cy.get('input[name="ccv_api_key"]').type('123456')

        // Select 'SAVE' input
        cy.get('input[name="_save"]')
          .click()
    })

    it('Add CCV Upstream; Save and continue editing', () => {
        // Navigate to /core/ccvupstream/add
        cy.contains('a', 'Ccv upstreams').click();
        cy.contains('a', 'Add ccv upstream').click()

        // Enter CCV API Endpoint
        cy.get('input[name="ccv_api_endpoint"]').type('tests/test')

        // Select CCV API Endpoint Status
        cy.get('select[name="ccv_api_endpoint_status"]')
          .select('Inactive')
          .should('have.value', 'INACTIVE')
        
        // Enter CCV API Username
        cy.get('input[name="ccv_api_username"]').type('tester2')

        // Enter CCV API Password
        cy.get('input[name="ccv_api_password"]').type('p')

        // Enter CCV API Key
        cy.get('input[name="ccv_api_key"]').type('123456')

        // Select 'Save and continue editing' input
        cy.get('input[name="_continue"]')
          .click()

        // Ensure the url changed
        cy.url().should('match', /\/ccvupstream\/\d+\/change/)
        // Ensure that "Change ccv upstream" page is rendered correctly
        cy.get('#container #main #content-start #content h1')
          .should('have.text', 'Change ccv upstream')

        // Delete the current LCV Downstream
        cy.contains('a', 'Delete').click()

        // Click "Yes, I'm sure" button
        cy.get('#container #main #content-start #content')
          .find('form')
          .find('div')
          .find('input[type="submit"]')
          .click()
    })

    it('Add CCV Upstream; Save and add another', () => {
        // Navigate to /core/ccvupstream/add
        cy.contains('a', 'Ccv upstreams').click();
        cy.contains('a', 'Add ccv upstream').click()

        // Enter CCV API Endpoint
        cy.get('input[name="ccv_api_endpoint"]').type('tests/test')

        // Select CCV API Endpoint Status
        cy.get('select[name="ccv_api_endpoint_status"]')
          .select('Inactive')
          .should('have.value', 'INACTIVE')
        
        // Enter CCV API Username
        cy.get('input[name="ccv_api_username"]').type('tester3')

        // Enter CCV API Password
        cy.get('input[name="ccv_api_password"]').type('p')

        // Enter CCV API Key
        cy.get('input[name="ccv_api_key"]').type('123456')

        // Select 'Save and continue editing' input
        cy.get('input[name="_addanother"]')
          .click()

        // Ensure the url stayed the same
        cy.url().should('include', '/admin/core/ccvupstream/add')
        // Ensure that "Add ccv upstream" page is rendered correctly
        cy.get('#container #main #content-start #content h1')
          .should('have.text', 'Add ccv upstream')
    })

    it('Delete CCV Upstream', () => {
        cy.contains('a', 'Ccv upstreams').click();
        cy.get('#container #main #content-start #content #content-main #changelist .changelist-form-container form')
          .find('.results')
          .find('table')
          .find('tbody')
          .find('tr')
          .each(($row) => {
            cy.wrap($row)
              .find('td.action-checkbox')
              .find('input[type="checkbox"]')
              .check()  // Check the checkbox (set it to true)
          })

        // Select "Delete selected users" from the drop-down menu
        cy.get('.actions')
          .find('select[name="action"]')
          .select('Delete selected ccv upstreams')
          .should('have.value', 'delete_selected')

        // Click "Go" button
        cy.get('.actions')
          .find('button[type="submit"]')
          .click()

        // Click "Yes, I'm sure" button
        cy.get('#container #main #content-start #content')
          .find('form')
          .find('div')
          .find('input[type="submit"]')
          .click()
    })
})