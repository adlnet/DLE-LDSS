 import { localLogin } from './helpers/localLogin';

describe('userspage', () => {
    beforeEach(() => {
      cy.wait(2000)
      const url = "/admin/users"

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
    })
  
    // afterEach(() => {
    //   // Clean up by deleting the user created during the test
    //   cy.removeUser("test@email.com")
    // });

    // + Add button tested in add user tests
  
    it('Navigate from /admin/users to /users/customuser', () => {
      // Click the " Change" button
      cy.get('#container #main #content-start #content #content-main .app-users table')
        .should('exist')  
        .contains('a', 'Change')
        .click()
      cy.get('#container #main #content-start #content h1').should('have.text', 'Select user to change')
    })
  
    // it('Add user; SAVE', () => {
    //   // Navigate to /admin/users/customuser/add
    //   cy.get('#container #main #content-start #content #content-main .app-users table')
    //       .find('a[href$="/admin/users/customuser/add/"]')
    //       .click()
  
    //   // Enter email address
    //   cy.get('input[name="username"]').type('test@email.com')
  
    //   // Enter password
    //   cy.get('input[name="password1"]').type('abct1zyx')
  
    //   // Confirm password
    //   cy.get('input[name="password2"]').type('abct1zyx')
  
    //   // Select 'SAVE' input
    //   cy.get('input[name="_save"]')
    //       .click()
  
    //   // Ensure the url changed
    //   cy.url().should('match', /\/customuser\/\d+\/change/)
    //   // Ensure that "Change user" page is rendered correctly
    //   cy.get('#container #main #content-start #content h1')
    //   .should('have.text', 'Change user')
  
    //   // Enter first name
    //   cy.get('input[name="first_name"]').type('Test')
  
    //   // Enter last name
    //   cy.get('input[name="last_name"]').type('Test')
  
    //   // Enter email address
    //   cy.get('input[name="email"]').type('test@email.com')
  
    //   // Select permissions
    //   cy.get('input[name="is_active"]')
    //       .uncheck(); // Check the checkbox (set it to false)
    //   cy.get('input[name="is_staff"]')
    //       .check() // Check the checkbox (set it to true)
    //   cy.get('input[name="is_superuser"]')
    //       .check() // Check the checkbox (set it to true)
  
    //   // Add new group (this maybe isn't implemented...)
  
    //   // Search available groups
    //   cy.get('input[id="id_groups_input"]').type('testers')
  
    //   // Find "Move to Chosen groups" arrow
    //   cy.contains('a', 'Choose')
    //     .should('exist')
  
    //   // Search chosen groups
    //   cy.get('input[id="id_groups_selected_input"]')
  
    //   // Find "Move to Available groups" arrow
    //   cy.contains('a', 'Remove')
    //     .should('exist')
  
    //   // Select Permissions click "Choose all"
    //   cy.get('#container #main #content-start #content #content-main')
    //   cy.get('form')
    //   cy.get('div')
    //   cy.get('fieldset').contains('h2', 'Permissions')
    //   cy.get('.field-user_permissions')
    //   cy.get('div')
    //   cy.get('.flex-container .related-widget-wrapper .selector .selector-available')
    //     .contains('a', 'Choose all').click()
  
    //   // Select Permissions click "Remove all"
    //   cy.get('#container #main #content-start #content #content-main')
    //   cy.get('form')
    //   cy.get('div')
    //   cy.get('fieldset').contains('h2', 'Permissions')
    //   cy.get('.field-user_permissions')
    //   cy.get('div')
    //   cy.get('.flex-container .related-widget-wrapper .selector #id_user_permissions_selector_chosen')
    //     .contains('a', 'Remove all').click()
  
    //   // Select "SAVE"
    //   cy.get('input[name="_save"]')
    //       .click()
    // })
  
    // it('Add user; Save and add another', () => {
    //   // Navigate to /admin/users/customuser/add
    //   cy.get('#container #main #content-start #content #content-main .app-users table')
    //       .find('a[href$="/admin/users/customuser/add/"]')
    //       .click()
  
    //   // Enter email address
    //   cy.get('input[name="username"]').type('test@email.com')
  
    //   // Enter password
    //   cy.get('input[name="password1"]').type('abct1zyx')
  
    //   // Confirm password
    //   cy.get('input[name="password2"]').type('abct1zyx')
  
    //   // Select 'Save and add another' input
    //   cy.get('input[name="_addanother"]')
    //       .click()
  
    //   // Ensure the url stayed the same
    //   cy.url().should('include', '/admin/users/customuser/add')
    //   // Ensure that "Add user" page is rendered correctly
    //   cy.get('#container #main #content-start #content h1')
    //   .should('have.text', 'Add user')
    // })
  
    // it('Add user; Save and continue editing', () => {
    //   // Navigate to /admin/users/customuser/add
    //   cy.get('#container #main #content-start #content #content-main .app-users table')
    //       .find('a[href$="/admin/users/customuser/add/"]')
    //       .click()
  
    //   // Enter email address
    //   cy.get('input[name="username"]').type('test@email.com')
  
    //   // Enter password
    //   cy.get('input[name="password1"]').type('abct1zyx')
  
    //   // Confirm password
    //   cy.get('input[name="password2"]').type('abct1zyx')
  
    //   // Select 'Save and continue editing' input
    //   cy.get('input[name="_continue"]')
    //       .click()
  
    //   // Ensure the url changed
    //   cy.url().should('match', /\/customuser\/\d+\/change/)
    //   // Ensure that "Change user" page is rendered correctly
    //   cy.get('#container #main #content-start #content h1')
    //   .should('have.text', 'Change user')
    // })
  });