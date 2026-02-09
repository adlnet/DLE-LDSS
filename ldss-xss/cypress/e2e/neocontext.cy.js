import { localLogin } from './helpers/localLogin';

describe('neocontextpage', () => {
    beforeEach(() => {
      cy.wait(2000)
      const url = "/admin/core/neocontext/"

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

      cy.contains('a', 'Neo context').click();
    })

    it('Add Neo Context +', () => {
        // Navigate to /core/neocontext/add
        cy.contains('a', 'Add neo context').click()
        cy.contains('Add neo context').should('be.visible')
    })

    it('Add Neo Context', () => {
        cy.contains('a', 'Add neo context').click()
        
        // Ensure django_id is not empty
        cy.get('input[name="django_id"]').should('not.have.value', '')

        // Ensure context is empty
        cy.get('.readonly').first().should('have.value', '')

        // Ensure context description is empty
        cy.get('.readonly').eq(1).should('have.value', '')

        // Ensure save buttons exist
        cy.get('input[name="_save"]').should('exist')
        cy.get('input[name="_addanother"]').should('exist')
        cy.get('input[name="_continue"]').should('exist')
    })

    // (Currently this results in a Server Error 500)
    // it('Delete Neo Context', () => {
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

    //     // Select "Delete selected neo contexts" from the drop-down menu
    //     cy.get('.actions')
    //       .find('select[name="action"]')
    //       .select('Delete selected neo contexts')
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