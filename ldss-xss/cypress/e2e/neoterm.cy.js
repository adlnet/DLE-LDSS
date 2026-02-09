import { localLogin } from './helpers/localLogin';

describe('neotermpage', () => {
    beforeEach(() => {
      cy.wait(2000)
      const url = "/admin/core/neoterm/"

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

      cy.contains('a', 'Neo term').click();
    })

    it('Add Neo Term +', () => {
        // Navigate to /core/neoterm/add/
        cy.contains('a', 'Add neo term').click()
        cy.contains('Add neo term').should('be.visible')
    })

    it('Add Neo Term; SAVE', () => {
        // Navigate to /core/neoterm/add/
        cy.contains('a', 'Add neo term').click()
    
        // Enter lcvid
        cy.get('input[name="lcvid"]').type('123')
    
        // Enter alias
        cy.get('input[name="alias"]').type('test')

        // Enter definition
        cy.get('input[name="definition"]').type('a term for testing')

        // Enter context
        cy.get('input[name="context"]').type('testing')

        // Enter context description
        cy.get('input[name="context_description"]').type('running a test')
    
        // Select 'SAVE' input
        // (not implemented yet)
        // cy.get('input[name="_save"]')
        //   .click()
    })
    
    // it('Add Neo Term; Save and continue editing', () => {
    //     // Navigate to /core/neoterm/add/
    //     cy.contains('a', 'Add neo term').click()
    
    //     cy.get('input[name="lcvid"]').type('456')
    //     cy.get('input[name="alias"]').type('test')
    //     cy.get('input[name="definition"]').type('a term for testing')
    //     cy.get('input[name="context"]').type('testing')
    //     cy.get('input[name="context_description"]').type('running a test')
    
    //     // Select 'Save and continue editing' input
    //     cy.get('input[name="_continue"]')
    //       .click()

    //     // Results in redirect to /admin
    //     // Shows error indicating that neo alias doesn't exist

    //     // Can't test delete button because of redirect
    
    //     // Ensure the url changed
    //     cy.url().should('match', /\/neoterm\/\d+\/change/)
    //     // Ensure that "Change neo term" page is rendered correctly
    //     cy.get('#container #main #content-start #content h1')
    //       .should('have.text', 'Change neo term')
    
    //     // Delete the current Neo Term
    //     cy.contains('a', 'Delete').click()
    
    //     // Click "Yes, I'm sure" button
    //     cy.get('#container #main #content-start #content')
    //       .find('form')
    //       .find('div')
    //       .find('input[type="submit"]')
    //       .click()
    // })
    
    // it('Add Neo Term; Save and add another', () => {
    //     // Navigate to /core/neoterm/add/
    //     cy.contains('a', 'Add neo term').click()
    
    //     // Select 'Save and add another' input
    //     cy.get('input[name="_addanother"]')
    //       .click()
    
    //     // Ensure the url stayed the same
    //     cy.url().should('include', '/admin/core/neoterm/add')
    //     // Ensure that "Add neo term" page is rendered correctly
    //     cy.get('#container #main #content-start #content h1')
    //       .should('have.text', 'Add neo term')
    // })
    
    // it('Delete Neo Term', () => {
    //     cy.get('#container #main #content-start #content #content-main #changelist .changelist-form-container form')
    //       .find('.results')
    //       .find('table')
    //       .find('tbody')
    //       .find('tr')
    //       .each(($row) => {
    //         cy.wrap($row)
    //           .find('td.action-checkbox')
    //           .find('input[type="checkbox"]')
    //           .check()  // Check the checkbox (set it to true)
    //       })
    
    //     // Select "Delete selected neo term" from the drop-down menu
    //     cy.get('.actions')
    //       .find('select[name="action"]')
    //       .select('Delete selected neo terms')
    //       .should('have.value', 'delete_selected')
    
    //     // Click "Go" button
    //     cy.get('.actions')
    //       .find('button[type="submit"]')
    //       .click()
    
    //     // Click "Yes, I'm sure" button
    //     cy.get('#container #main #content-start #content')
    //       .find('form')
    //       .find('div')
    //       .find('input[type="submit"]')
    //       .click()
    // })

    it('Confirm Select Page', () => {
        // Confirm Buttons
        cy.contains('a', 'CSV Upload').should('exist')
        cy.contains('a', 'Export Terms(JSON)').should('exist')
        cy.contains('a', 'Export Terms(CSV)').should('exist')
    })
})