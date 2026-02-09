import { localLogin } from './helpers/localLogin';

describe('neoaliaspage', () => {
    beforeEach(() => {
      cy.wait(2000)
      const url = "/admin/core/neoalias/"

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

      cy.contains('a', 'Neo alias').click();
    })

    it('Add Neo Alias +', () => {
        // Navigate to /admin/core/neoalias/add
        cy.contains('a', 'Add neo alias').click()
        cy.contains('Add neo alias').should('be.visible')
    })

    it('Add Neo Alias; SAVE', () => {
        // Navigate to /core/neoalias/add
        cy.contains('a', 'Add neo alias').click()

        // Confirm django_id is not empty
        cy.get('input[name="django_id"]').should('not.have.value', '')

        // Enter alias
        cy.get('input[name="alias"]').type('test')

        // Select 'SAVE' input
        cy.get('input[name="_save"]')
          .click()
    })

    it('Add Neo Alias; Save and continue editing', () => {
        // Navigate to /core/neoalias/add
        cy.contains('a', 'Add neo alias').click()

        // Enter alias
        cy.get('input[name="alias"]').type('test2')

        // Select 'Save and continue editing' input
        cy.get('input[name="_continue"]')
          .click()

        // Results in redirect to /admin
        // Shows error indicating that neo alias doesn't exist

        // Can't test delete button because of redirect
    })

    it('Add Neo Alias; Save and add another', () => {
        // Navigate to /core/neoalias/add
        cy.contains('a', 'Add neo alias').click()

        // Enter alias
        cy.get('input[name="alias"]').type('test3')

        // Select 'Save and continue editing' input
        cy.get('input[name="_addanother"]')
          .click()

        // Ensure the url reloaded
        cy.get('#container #main #content-start #content h1')
          .should('have.text', 'Add neo alias')
    })

    // (Currently this results in a Server Error 500)
    // it('Delete Neo Alias', () => {
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

    //     // Select "Delete selected neo alias" from the drop-down menu
    //     cy.get('.actions')
    //       .find('select[name="action"]')
    //       .select('Delete selected neo aliass')
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
})