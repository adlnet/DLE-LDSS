import { localLogin } from './helpers/localLogin';

describe('lcvdownstreampage', () => {
  beforeEach(() => {
    cy.wait(2000)
    const url = "/admin/core/lcvdownstream/"

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

    cy.contains('a', 'Lcv downstreams').click();
  })

  it('Add LCV Downstream +', () => {
    // Navigate to /core/lcvdownstream/add/
    cy.contains('a', 'Add lcv downstream').click()
    cy.contains('Add lcv downstream').should('be.visible')
  })

  it('Add LCV Downstream; SAVE', () => {
    // Navigate to /core/lcvdownstream/add/
    cy.contains('a', 'Add lcv downstream').click()

    // Enter LCV API Endpoint
    cy.get('input[name="lcv_api_endpoint"]').type('tests/test')

    // Enter LCV API Key
    cy.get('input[name="lcv_api_key"]').type('123456')

    // Select LCV API Endpoint Status
    cy.get('select[name="lcv_api_endpoint_status"]')
      .select('Active')
      .should('have.value', 'ACTIVE')
      .select('Inactive')
      .should('have.value', 'INACTIVE')

    // Select 'SAVE' input
    cy.get('input[name="_save"]')
      .click()
  })

  it('Add LCV Downstream; Save and continue editing', () => {
    // Navigate to /core/lcvdownstream/add/
    cy.contains('a', 'Add lcv downstream').click()

    // Enter LCV API Endpoint
    cy.get('input[name="lcv_api_endpoint"]').type('tests/test2')

    // Enter LCV API Key
    cy.get('input[name="lcv_api_key"]').type('123456')

    // Select LCV API Endpoint Status
    cy.get('select[name="lcv_api_endpoint_status"]')
      .select('Inactive')
      .should('have.value', 'INACTIVE')

    // Select 'Save and continue editing' input
    cy.get('input[name="_continue"]')
      .click()

    // Ensure the url changed
    cy.url().should('match', /\/lcvdownstream\/\d+\/change/)
    // Ensure that "Change lcv downstream" page is rendered correctly
    cy.get('#container #main #content-start #content h1')
      .should('have.text', 'Change lcv downstream')

    // Delete the current LCV Downstream
    cy.contains('a', 'Delete').click()

    // Click "Yes, I'm sure" button
    cy.get('#container #main #content-start #content')
      .find('form')
      .find('div')
      .find('input[type="submit"]')
      .click()
  })

  it('Add LCV Downstream; Save and add another', () => {
    // Navigate to /core/lcvdownstream/add/
    cy.contains('a', 'Add lcv downstream').click()

    // Enter LCV API Endpoint
    cy.get('input[name="lcv_api_endpoint"]').type('tests/test3')

    // Enter LCV API Key
    cy.get('input[name="lcv_api_key"]').type('123456')

    // Select LCV API Endpoint Status
    cy.get('select[name="lcv_api_endpoint_status"]')
      .select('Inactive')
      .should('have.value', 'INACTIVE')

    // Select 'Save and add another' input
    cy.get('input[name="_addanother"]')
      .click()

    // Ensure the url stayed the same
    cy.url().should('include', '/admin/core/lcvdownstream/add')
    // Ensure that "Add lcv downstream" page is rendered correctly
    cy.get('#container #main #content-start #content h1')
      .should('have.text', 'Add lcv downstream')
  })

  it('Delete LCV Downstream', () => {
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

    // Select "Delete selected lcv downstream" from the drop-down menu
    cy.get('.actions')
      .find('select[name="action"]')
      .select('Delete selected lcv downstreams')
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