import { localLogin } from './helpers/localLogin';

describe('userssection', () => {
    beforeEach(() => {
      cy.wait(2000)

      // If running CI use visitWithJWT, else use completeLogin
      if (Cypress.env('isCI')) {
          const jwt = Cypress.env('adminJWT')
          if (!jwt) {
              throw new Error('JWT is missing in CI environment')
          }
          cy.visitWithJWT("/ldss-xss/admin", jwt)
      } else {
          // Call completeLogin command
          localLogin("admin@email.com", "password");
      }
    })

    it('Navigate from /admin to /users/customuser', () => {
      // Navigate to /users/customuser
      cy.get('#container #main #content-start #content #content-main .app-users table')
        .find('a[href$="/admin/users/customuser/"]')
        .first()
        .click()
      cy.contains('Select user to change').should('be.visible')
    })
  
    // it('Navigate from /admin to /users/customuser/add', () => {
    //   // Click the "+ Add" button
    //   cy.get('#container #main #content-start #content #content-main .app-users table')
    //     .should('exist')  
    //     .contains('a', 'Add')
    //     .click()
  
    //   // Assert that the user is redirected to /customuser/add/
    //   cy.url().should('include', '/customuser/add')
  
    //   // Check if a specific element is visible on the dashboard
    //   cy.contains('Add user').should('be.visible')
    // })
  
    it('Navigate from /admin to /users/customuser', () => {
      // Click the " Change" button
      cy.get('#container #main #content-start #content #content-main .app-users table')
        .should('exist')  
        .contains('a', 'Change')
        .click()
      cy.get('#container #main #content-start #content h1').should('have.text', 'Select user to change')
    })
  });