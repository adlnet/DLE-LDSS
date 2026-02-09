/// <reference types="Cypress" />
// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })

Cypress.Commands.add('completeLogin', (email, password) => {
  // Utilize sessions to maintain login credentials between tests
  cy.session('user-session', () => {
    cy.visit("/admin")
    cy.get('input[name="username"]').type(email)
    cy.get('input[name="password"]').type(password)
    cy.get('input[value="Log in"]').click()

    // Wait until admin loads
    cy.url().should('include', '/admin')
    cy.contains('h1', 'Site administration').should('be.visible')
  }, {
    cacheAcrossSpecs: false // Ensures the session is reset between different spec files
  })
})

Cypress.Commands.add('visitWithJWT', (url, jwtToken) => {
  cy.intercept('GET', '**/*', (req) => {
    req.headers['authorization'] = `Bearer ${jwtToken}`
  })
  cy.intercept('POST', '**/*', (req) => {
    req.headers['authorization'] = `Bearer ${jwtToken}`
  })
  cy.intercept('HEAD', '**/*', (req) => {
    req.headers['authorization'] = `Bearer ${jwtToken}`
  })
  cy.intercept('DELETE', '**/*', (req) => {
    req.headers['authorization'] = `Bearer ${jwtToken}`
  })
  cy.intercept('PUT', '**/*', (req) => {
    req.headers['authorization'] = `Bearer ${jwtToken}`
  })
  return cy.visit({
    url: url,
    auth: {
      bearer: jwtToken
    },
    failOnStatusCode: false,
  })
})

Cypress.Commands.add('removeUser', (user_email_address) => {
  // Navigate to /users/customuser
  cy.visit("/admin/users/customuser/")
  cy.contains('Select user to change')

  cy.get('#container #main #content-start #content #content-main #changelist .changelist-form-container form')
    .find('.results')
    .find('table')
    .find('tbody')
    .find('tr')
    .each(($row) => {
      // Try to find the <td> with class 'field-email' that contains user_email_address
      cy.wrap($row)
        .find('th.field-username')
        .then(($td) => {
          // If user_email_address is found within the <td>, check the checkbox
          if ($td.text().includes(user_email_address)) {
            cy.wrap($row)
              .find('td.action-checkbox')
              .find('input[type="checkbox"]')
              .check()  // Check the checkbox (set it to true)
          }
        })
    })

  // Select "Delete selected users" from the drop-down menu
  cy.get('.actions')
    .find('select[name="action"]')
    .select('Delete selected users')
    .should('have.value', 'delete_selected')

  // Click "Go" button
  cy.get('.actions')
    .find('button[type="submit"]')
    .click()

  // /users/customuser/ page reloads
  // Click "Yes, I'm sure" button
  cy.get('#container #main #content-start #content')
    .find('form')
    .find('div')
    .find('input[type="submit"]')
    .click()
})

// 'Published' is a boolean
Cypress.Commands.add('addTermSet', (term_set_name, published) => {
  cy.visit("/admin/core/termset/add/")
  cy.get('input[name="name"]').type(term_set_name)
  cy.get('input[name="version"]').type('1.2.3')

  if (published) {
    cy.get('select[name="status"]')
      .select('published')
  } else {
    cy.get('select[name="status"]')
      .select('retired')
  }

  // Select 'SAVE' input
  cy.get('input[name="_save"]')
  .click()
})
